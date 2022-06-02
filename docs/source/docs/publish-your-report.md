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
# Pull from DockerHub
docker pull nordata/biovis-report-viewer:v0.5
```

## Prepare the compiled report

The compiled report contains a series of html, data, css, and javascript files, as shown in the following figure

![Report HTML](/assets/images/report_html.png)

### Get compiled report from other researchers

### Compile your own report

Please follow the [`Write Your Report`](/docs/write-your-report/#build-your-report-for-publishing-or-sharing-to-other-researchers) if you need to compile your report.

### Download the example report

Download <a href="/assets/report_html.zip">the example report</a>. After downloading, please unzip the report_html.zip file.

## View the report

We assume that you have downloaded the sample report and unzipped it.

```
docker run -d -v report_html:/srv/shiny-server/ -v log:/var/log/shiny-server -p 3838:3838 nordata/biovis-report-viewer:v0.5
```

Open your chrome browser and access the [http://localhost:3838](http://localhost:3838)