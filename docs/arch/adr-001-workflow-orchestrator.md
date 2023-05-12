# Workflow Orchestrator for Kubernetes - Architecture Decision Record

## Context

We need to select a suitable replacement for the way we use AWS Step Functions
in [cirrus-geo](https://github.com/cirrus-geo/cirrus-geo) projects.

### Key requirements

* Specify reusable tasks from containers
* Ability to run individual tasks with different hardware resources
  * size instance appropriately for task
  * pass any special hardware resources to task, e.g., GPUs
* Some facility for integration with state/events database(s) for payload state
  tracking
* Must allow implementation of workflow chaining
* Ideally allow implementation of workflow callbacks

## Possible contenders

We started by building a list of a number of possible contenders with the
intent to narrow down the list to 2-3 for a more in-depth selection process.

### Prefect

* Uses Python to define workflows
* Has plugin for k8s, runs a flow as a kubernetes job
  * It seems that a flow is equivalent to what we would call a workflow, but
    also supports “subflows”. Each flow can be executed in its own container,
    but doesn’t support containers per task unless using the docker task
    plugin.
    * Note that prefect has two API versions, v1 and v2. This forum post has
      with a lot of info about the former, but not much about the latter: [Can
      Prefect run each task in a different Docker
      container?](https://discourse.prefect.io/t/can-prefect-run-each-task-in-a-different-docker-container/434)
  * It seems like containers per task is not really recommended.
  * The idea of a “lambda” task, at least for those without non-standard
    dependencies, is well accommodated by this “container-per-flow” model, such
    that we don’t incur the overhead of individual task containers where not
    explicitly required.
  * It is unclear if prefect would support arbitrary task containers out of the
    box
    * Ideally we could have a defined task interface, and it wouldn’t matter
      how that container is implemented, i.e., we could use something other
      than python.
  * Seems like this is could be a fairly leaky abstraction--prefect is pushing
    certain ideas on the user about tasks and whatnot, but they don’t
    necessarily align with how we’ll need to manage resources, so then we have
    to think past the prefect abstractions.
  * Seems well oriented to describing simple or complex workflows, but we might
    struggle to model tasks as containers in an effective manner.
  * Can use postgres for tracking state
  * Open core, not fully open source

### Dagster

* Uses Python to define workflows
* Has plugin to launch runs as k8s jobs, as well as a helm chart for deploying
  into k8s
  * This seems to indicate an entire workflow (run) would run within a single
    container (as a job).
  * Not sure if, like prefect, we can do nested runs and whatnot to work around
    this problem.
    * Again, a leaky abstraction
* Definitely feels like it is more ETL data-focused, and less
  workflow-oriented. Not that it doesn’t support workflows, but that doesn’t
  seem to be its strong suit. The ergonomics might push against how we want to
  use it.
  * Datasets, which it calls assets, are the first-class abstraction. It is
    something like a declarative framework for specifying what data you want,
    rather than a framework to build an imperative workflow to process some
    input into its outputs.
  * I think we want the workflows to present something of a declarative
    interface, but I feel to make that happen the workflows themselves need to
    be implemented imperatively in a way that supports the desired interface.
* Postgres or sqlite for state tracking

### Argo Workflows

* Kubernetes native
* Workflows declared in yaml as k8s resources
* Feels very much like step functions
  * Limited logic/control available within the workflow declaration itself
  * But templating feels like a profound improvement over step functions
    * Allow code reuse and some modularization
* Artifact object storage is handled by Argo
  * We can simply write outputs to local storage, and Argo can be configured to upload those files to the object storage.
* Steps support outputs, which can be referenced in later steps
  * I don’t think we’ll need pre- or post-batch
* “Simple lambdas” can be achieved with scripts, and are not strictly python
  * But still have the overhead of spinning up a dedicated pod for execution
  * Also look at plugins

### Apache Airflow

* Can run on top of kubernetes, but similar issues to all the other k8s
  non-native solutions
* Overwhelming opinion is it is antiquated and the cruft makes it rather
  difficult to use
* We do have some experience with a pipeline built on top of it, but it was not
  positive

### Luigi

* Feels very much like Prefect, except old and crusty API/dev experience
* Going to run into the same problems running on k8s

### Kubeflow

* Seems more oriented to ML experimentation and whatnot
  * It _might_ be a perfectly great option for our use case, but getting pass
    the ML bias in the docs is difficult
* Does have a separate pipelines piece that allows configuring workflows in
  python
  * Appears it uses Argo Workflows under the covers
  * Worth some additional investigation if we find the Argo yaml limiting
  * An unstable v2 is in the works, so seems like a bad time to pick up v1 or
    v2

### MLflow

* From a cursory read of the docs, this is very much focused on ML models and
  training, and is not a good fit for our use case (it might work, but with a
  bunch of stuff we really don’t need layered on top complicating things).

### Apache Beam

* Pipelines can be written in multiple languages (at least those with an SDK,
  being JVM langs, python, and go) that targets multiple backend runners. This
  allows a pipeline to be portable.
* What this means though is beam doesn’t actually solve the problem of running
  a workflow.
  * Looks like to get Beam running on k8s the solution is Apache Flink.
* All it really seems to be is an abstraction layer to allow workflows to be
  written once and run in many places.
  * In practice might not be a big deal for FD users
  * And doesn’t run on step functions or other cloud managed services
  * This all feels super enterprise-y and complicated
    * May mean it has better runtime semantics than others (Flink claiming
      things like “Fault-tolerance with exactly-once processing guarantees”).
    * Also means this is likely not a "fast" solution
  * Likely means it can't solve the "how to run tasks as individual containers
    on k8s" problem without leaking significantly

### Calrissian/StreamFlow (CWL)

As these options are built on CWL, it seems important to start with some points
about CWL itself:

* CWL is the Common Workflow Language. It exists as a cross-platform standard
  for specifying workflows.
* The CWL heritage seems to be academic HPC, and has a rather academic feel to
  it.
* The idea of a standardized workflow language is compelling and worthy of
  consideration.
* No error handling within the spec for some reason (from what I could tell)
* Different implementations for different platforms; see
  [Implementations](https://www.commonwl.org/implementations/)
* People have developed different grammars that compile down to CWL, for
  example [cwl-ex](https://github.com/common-workflow-lab/cwl-ex)

[Calrissian](https://github.com/Duke-GCB/calrissian) was mentioned by others in
the STAC community as something of interest for running workflows on k8s:

* Still in early development
* Uncertain how well it tracks the CWL spec and which versions are supported
* Single focus is on running CWL on k8s
* Is used in production by some

[StreamFlow](https://streamflow.di.unito.it/) is another option that has k8s
among many supported targets:

* Maintained by an academic HPC organization, so that is its focus
* Has a rather antiquated feel

Generally, my perception is that CWL and its implementations are great in
theory but lack the weight of big tech behind them and therefore will have
crusty edges and poor user or developer experience. But it could be viewed as
the workflow language component that I’ve wanted to create from the idea of the
STAC workflow spec as unified interface for processing workflows that can run
across multiple platforms/implementations.

I think CWL belongs one level up from the orchestrator, and that view is
supported by the fact that the OGC Process API Part III spec for workflows uses
CWL as the language with which to define a chain of processes.

## Deep dive

Reviewing the list above, we ultimately narrowed down the pool to three
contenders, which we reviewed in depth. The summary pro/con lists are provided
here.

### Argo Workflows

* Pros
  * Most importantly, Argo is meant for kubernetes. It runs as a K8s Custom
    Resource Definitions (CRD).
  * It natively integrates with other K8s services like volumes, secrets,
    Role-Based Access Control etc.
  * Each step in a workflow executes in a separate container in a separate Pod.
  * It is easy to pass variables (parameters) or artifacts between different
    steps of a workflow that are running in separate Pods in a cluster
  * It is easy to pass resource requests and limits (CPU/memory) to different
    steps
  * It is fully open-source
  * It is easy to deploy and use
  * Documentation is sufficiently complete
  * Great integration with Argo Events, an event-based ecosystem
* Cons
  * Significant latency overhead associated with spinning up a pod for each
    step in a workflow
  * Cannot run any processing natively within the workflow, so we don't have a
    good way to emulate cirrus lambda tasks

### Prefect

* Pros
  * Lightweight processing available within the workflow runner itself, on par
    with our use of cirrus lambda tasks
* Cons
  * It is not fully open-source, but open core. Some features are only
    available via a subscription (Prefect Cloud).
  * We might get constrained later on in development due to lack of needed
    functionality due to the open core nature of Prefect
  * It is unclear how queues are handled in the backend and what would happen
    when one fails.
  * Since it has two versions (v1 and v2) that have a dramatic difference in
    functionality yet also have their own distinctly useful methods, one is
    stuck with choosing between one or the other
  * Documentation on how to deploy onto K8s is lacking
  * Even after creating a separate Deployment for each task, it is unclear how
    to pass variables or payloads between tasks running in separate Pods
  * Will require more initial configuration than Argo
  * Although it has support for other orchestrators outside of K8s, these are
    not relevant to what we are doing

### Apache Airflow

* Pros
  * None relative to our experience with the other options
* Cons
  * Heavy initial configuration effort needed in a production environment
  * Not enough official documentation on how to get started with running on K8s
  * The documentation that is there is also conflicting in some places, maybe
    due to version changes
  * Unclear how to pass variables or artifacts (files) between tasks running in
    separate Pods in K8s
  * Even outside K8s, there is limited support via XCom in terms of data size
    for passing variables and artifacts between steps
  * DAGS are static, they cannot process an arbitrary number of tasks in
    parallel at runtime (i.e. no dynamic fan-in, fan-out like Argo)
  * Not intended solely for running containers on K8s unlike Argo; supports a
    broad variety of other operators apart from Kubernetes; this makes it less
    specialized for K8s deployment
  * The parallelism of a workflow is limited by the number of worker nodes,
    unlike Argo where the parallelism is not limited since each task runs as a
    container

## Decision

Winner: Argo Workflows

Argo is the only one of these three candidates that does what we need for SWOOP
out of the box. The only obvious negative from our investigation is the
overhead associated with each step running in a different pod and the
consequent latency penalty. This may be possible to mitigate with plugins,
though we may need to implement support for certain plugin types to get the
functionality we are after, if the latency becomes a penalty.
