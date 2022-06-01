# The build-stage image:
FROM continuumio/miniconda3 AS build

# Install conda-pack:
RUN conda install -c conda-forge conda-pack mamba

# Install the package as normal:
COPY environment.yml .
RUN mamba env create -f environment.yml

# Use conda-pack to create a standalone enviornment
# in /venv:
RUN conda-pack -n biovis-report -o /tmp/env.tar && \
  mkdir /venv && cd /venv && tar xf /tmp/env.tar && \
  rm /tmp/env.tar

# We've put venv in same path it'll be in final image,
# so now fix up paths:
RUN /venv/bin/conda-unpack

# The runtime-stage image; we can use Debian as the
# base image since the Conda env also includes Python
# for us.
FROM rocker/shiny:3.6.3 AS runtime

WORKDIR /srv/shiny-server/
# Remove the old R binary
RUN cp /usr/local/bin/R /usr/local/bin/R-3.6.3
RUN ln -s /venv/bin/R /usr/local/bin/R -f
env PATH=/venv/bin:$PATH

# Copy /venv from the previous stage:
COPY --from=build /venv /venv
