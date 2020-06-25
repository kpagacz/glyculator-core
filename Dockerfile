FROM ubuntu:18.04

RUN apt-get update \ 
	&& apt-get install -y --no-install-recommends \
	    apt-utils \
		ed \
		less \
		locales \
		vim-tiny \
		wget \
		ca-certificates \
		apt-transport-https \
		gsfonts \
		gnupg2 \
		curl \
        default-jre \
        default-jdk \
	&& rm -rf /var/lib/apt/lists/*

RUN echo "en_US.UTF-8 UTF-8" >> /etc/locale.gen \
	&& locale-gen en_US.utf8 \
	&& /usr/sbin/update-locale LANG=en_US.UTF-8

ENV LC_ALL en_US.UTF-8
ENV LANG en_US.UTF-8

# note the proxy for gpg
RUN curl -sSL 'http://keyserver.ubuntu.com/pks/lookup?op=get&search=0xE084DAB9' | gpg --import
RUN gpg -a --export E084DAB9 | apt-key add -
RUN curl -sSL 'http://keyserver.ubuntu.com/pks/lookup?op=get&search=0x51716619E084DAB9' | gpg --import
RUN gpg -a --export 51716619E084DAB9 | apt-key add -
   
ENV R_BASE_VERSION 3.6.3
LABEL version=3.6.3

# Now install R and littler, and create a link for littler in /usr/local/bin
# Also set a default CRAN repo, and make sure littler knows about it too
RUN DEBIAN_FRONTEND="noninteractive" TZ="Europe/Paris" apt-get update \
	&& apt-get install -y --no-install-recommends \
		littler \
        r-cran-littler \
		r-base \
		r-base-dev \
		r-recommended \
        && echo 'options(repos = c(CRAN = "https://cloud.r-project.org/"), download.file.method = "libcurl")' >> /etc/R/Rprofile.site \
        && echo 'source("/etc/R/Rprofile.site")' >> /etc/littler.r \
	&& ln -s /usr/share/doc/littler/examples/install.r /usr/local/bin/install.r \
	&& ln -s /usr/share/doc/littler/examples/install2.r /usr/local/bin/install2.r \
	&& ln -s /usr/share/doc/littler/examples/installGithub.r /usr/local/bin/installGithub.r \
	&& ln -s /usr/share/doc/littler/examples/testInstalled.r /usr/local/bin/testInstalled.r \
	&& install.r docopt \
	&& rm -rf /tmp/downloaded_packages/ /tmp/*.rds \
	&& rm -rf /var/lib/apt/lists/* && \
    R -e "install.packages('xlsx')" && \
    R -e "install.packages('dplyr')" && \
    R -e "install.packages('ttutils')" && \
    R -e "install.packages('lubridate')" && \
    R -e "install.packages('stringr')" && \
    R -e "install.packages('ggplot2')" && \
    R -e "install.packages('MESS')" && \
    R -e "install.packages('data.table')" && \
    R -e "install.packages('shiny')" && \
    R -e "install.packages('shiny')" && \
    R -e "install.packages('shinythemes')" && \
    R -e "install.packages('rmarkdown')"

# shiny server adn rstudio
# RUN wget "https://download2.rstudio.org/rstudio-server-1.1.419-amd64.deb" && \
#     gdebi -n rstudio-server-1.1.419-amd64.deb

RUN wget "https://download3.rstudio.org/ubuntu-12.04/x86_64/shiny-server-1.5.5.872-amd64.deb" && \
    gdebi -n shiny-server-1.5.5.872-amd64.deb 

# app copy
COPY . /srv/shiny-server/glyculator
RUN chmod -R 755 /srv/shiny-server/
COPY shiny-conf /etc/shiny-server/shiny-server.conf

EXPOSE 3838

CMD ["/bin/bash"]