# SWOOP API Design - Architecture Decision Record

## Context

We are building an API for the STAC Workflow Open Orchestration Platform, with
the intent that it would be the interface for clients to interact with the
processing pipeline and state database. As an open source project for the
community, we want to leverage any existing API standards, specifications, or
best-practice patterns to ensure we have the greatest chance at making this
project as useful as possible (following in the example of the STAC API spec).

Ultimately, we want this API implementation to inform a new community API
specification for processing STAC items.

Note that a key aspect of this work will be supporting a processing pipeline
running on kubernetes.

### API Requirements

Using the existing [cirrus-geo](https://github.com/cirrus-geo/cirrus-geo)
project, its API, and the
[cirrus-mgmt](https://github.com/cirrus-geo/cirrus-mgmt) plugin to inform the
needs of this project, we come up with the following possible requirements:

* Process a payload
* Template a payload from deployment vars (like deployment name, S3 bucket
  name, etc)
* Perhaps this is a client-side feature using some /env endpoint that provides
  the deployment environment
* Get state for a payload ID
* Get execution input payload (from execution ID or payload ID)
* Get execution output payload (from execution ID or payload ID)
* Get execution state/details (from execution ID or payload ID)
* Get payload from S3 (from payload ID, perhaps this is redundant with “Get
  execution input payload” and also rather racy (last in wins))

We know we also need API endpoints to:

* Get list of all defined (active?) workflows
* Get all executions for a workflow
* Summarize counts (like current API)
* Get state change events

In this new k8s world, we also should see if we can add the following
implementation-specific features:

* Get logs

### Possible options

Three possible options come to mind for this API:

* base our work on the OGC Prcess API specification
* base our work on the OpenEO API specification
* do not base our work on any existing standard(s)

#### OGC Process API

* [OGC API - Processes home page](https://ogcapi.ogc.org/processes/)
* [OGC API - Processes - Part 1: Core
  Spec](https://docs.ogc.org/is/18-062r2/18-062r2.html)
* [OGC Processes - Overview](https://ogcapi.ogc.org/processes/overview.html)
* [OCG Processes API on
  SwaggerHub](https://app.swaggerhub.com/apis/OGC/ogcapi-processes-1-example-1/1.0.0)

This is a very simple spec. From the overview:

* Process endpoints
  * GET /processes

    Lists the processes this API offers.
  * GET /processes/{process-id}

    Returns a detailed description of a process.
  * POST /processes/{process-id}/execution

    Executes a process (asynchronous execution will create a new job). Inputs
    and outputs can be specified in a JSON document that needs to be sent in
    the POST body.

* Job management end-points (required for asynchronous execution, but optional
  for synchronous)
  * GET /jobs

    Returns the running and finished jobs.
  * GET /jobs/{job-id}

    Returns the status of a job.
  * DELETE /jobs/{job-id}

    Cancel a job execution.
  * GET /jobs/{job-id}/results

    Returns the result of a job.

Note that execution requires a mode parameter, which defines whether execution
is synchronous or asynchronous. With our use-case, synchronous execution makes
no sense, so we would only support the latter.

##### OGC Process API Part III: Workflows and Chaining

A draft specification exists for a new "workflows and chaining" extension to
the core OGC Process API spec. From the spec, it seems workflows here are about
chaining defined processes together, such that process request can have nested
process requests within it. Even nested calls to a remote process API are
supported.

At first glance this is both attractive and confusing for our use-case. But
after consideration, it becomes clear that what we are intending to expose to
the user regarding "workflows" is more akin to the definition of "processes" in
the core spec. Thus, this extension does not seem relevant to consider at the
moment.

#### OpenEO Spec

* [OpenEO home page](https://openeo.org/)
* [OpenEO interactive schema](https://openeo.org/documentation/1.0/developers/api/reference.html)

At first glance the OpenEO spec seems the same as OGC Process, as it has both
`/processes` and `/jobs`. However, the spec has way more features (like auth,
billing, price estimation, etc.) and appears intended to be used slightly
differently. For example, rather than `POST`ing to
`/processes/{process-id}/execution`, instead to create a new job you `POST` to
`/jobs` with the job definition. That doesn’t trigger processing until you also
`POST` to another endpoint specifically to start processing.

We don’t have to implement all API feature areas, as they are defined as a set
of optional conformance classes. So this could leave it open to add them in the
future, when and where they are deemed useful.

The list of available processes is standardized, and there’s some expectation
that backends will implement this standard set. User-defined processes are then
graphs of the processes chained together--much like a workflow in the OGC
Processes nomenclature. However, the model here appears to be a simple linear
flow like A → B → C, and doesn’t allow branching, conditionals, error handling,
etc.

#### Implementing our own

We could do this, but if either of the above options fit our use-case, then we
are forgoing compatibility with a community specification for no good reason.

OpenEO feels very much intended for a different use-case than ours. If we were
to adopt it, I think it would be rather misleading. OCG Processes is generic
enough that I don’t think it would be problematic in the same way.

## Decision

OGC Processes is generic enough to fit our use-case without compromising our
interface. We will be able to extend it with additional conformance classes
specific to our needs (for example, things like payload state caching), and we
can fit our STAC-based input/output payload format into the OCG Processes
input/output schemas due to their significant flexibility.

## Consequences

The API will use the term "process" for "workflow" and "job" for "workflow
execution". This is confusing to those with cirrus experience, and will
conflict with terminology used within swoop. But having a bit of confusion
there for workflow developers and operators is likely a small inconvenience at
most relative to the ability to base our API design off an existing community
spec.
