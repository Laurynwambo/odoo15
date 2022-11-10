FROM odoo:15.0
USER root
ENV DEBIAN_FRONTEND=noninteractive LANG=C.UTF-8
RUN apt-get update
COPY . /mnt/custom-addons
# RUN pip3 install -r . /mnt/requirements.txt
RUN pip3 install sphinx==1.2.3
RUN pip3 install mercurial==3.2.2
RUN pip3 install  sphinx-patchqueue==0.4.0
USER odoo
