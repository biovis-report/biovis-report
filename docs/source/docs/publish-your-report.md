## Install Docker

Please follow [the docs](https://docs.docker.com/get-docker/) for more details.

## Test your installation

```
docker -v

# Output (Similar with the following line)
Docker version 20.10.14, build a224086
```

## Pull the biovis-report-viewer

```
# Pull from GitHub Contianer Repository
docker pull ghcr.io/biovis-report/biovis-report-viewer:v0.5

# Or

# Pull from DockerHub
docker pull nordata/biovis-report-viewer:v0.5
```

## Get compiled report from other researchers or compile your own

The compiled report contains a series of html, data, css, and javascript files, as shown in the following figure

![Report HTML](/assets/images/report_html.png)

Please follow the [`Write Your Report`](/docs/write-your-report/#build-your-report-for-publishing-or-sharing-to-other-researchers) if you need to compile your report.
