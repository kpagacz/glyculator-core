FROM ubuntu:18.04

RUN apt-get install gnupg2 -y && \
    apt-key adv --keyserver keyserver.ubuntu.com \
    --recv-keys E298A3A825C0D65DFD57CBB651716619E084DAB9 && \
    echo "deb https://cloud.r-project.org/bin/linux/ubuntu bionic-cran35/" \
    | sudo tee -a /etc/apt/sources.list 
RUN apt-get update && \
    apt-get install r-base r-base-dev default-jre default-jdk gdebi-core git -y && \
    rm -rf /var/lib/apt/lists/* && \
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

CMD ["/usr/bin/shiny-server.sh"]