# Customized jenkins docker
# adding the plugins listed in plugins.txt
#
# See: 
#   https://wiki.jenkins-ci.org/display/JENKINS/Installing+Jenkins+with+Docker
#   https://hub.docker.com/_/jenkins/


FROM jenkins

COPY usr /usr
USER root
RUN usermod jenkins -G shadow &&\
    chage -d0 jenkins 

RUN /usr/local/bin/plugins.sh /usr/share/jenkins/plugins.txt
USER jenkins

#ENV JENKINS_OPTS --prefix=jenkins


