# Using `fastapi` as the API framework  - Architecture Decision Record

## Context

We are building an API in python, and as such:

1. would benefit significantly from the use of an API framework
1. have many options to choose from

As a result we need to pick a framework to use.

### Options

We could use many different options, but a short list might include:

* `django` with `django-rest-framework`
* `flask`
* `fastapi`

## Decision

We are going to use `fastapi` for a few key reasons:

* lightweight and performant
* automatically generates openapi docs
* in use in stac-fastapi (which we will also be using with this project)
* we are confident that it will work for our use-case with minimal friction

We didn't do anything to vet this decision beyond compiling the above list.
