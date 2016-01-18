# Jekyll development server. Monitor the source in the directory *site* and serve it
# including the drafts on port 80 for visualization.
#
FROM ubuntu:14.04.3

MAINTAINER Jean-Marc Guiraudet <jguiraudet@gmail.com>

WORKDIR /root

RUN	apt-get update &&\
	apt-get -y install git-core curl zlib1g-dev build-essential libssl-dev libreadline-dev libyaml-dev \
		   libsqlite3-dev sqlite3 libxml2-dev libxslt1-dev libcurl4-openssl-dev \
		   python-software-properties libffi-dev wget nodejs nginx &&\
	rm /usr/share/nginx/html/* &&\
	cd &&\
	wget http://ftp.ruby-lang.org/pub/ruby/2.2/ruby-2.2.3.tar.gz &&\
	tar -xzvf ruby-2.2.3.tar.gz &&\
	cd ruby-2.2.3/ &&\
	./configure &&\
	make &&\
	make install &&\
	cd &&\
	rm -fr ruby-2.2.3  ruby-2.2.3.tar.gz &&\
	ruby -v &&\
# Don't install documentation  
	echo "gem: --no-ri --no-rdoc" > ~/.gemrc &&\
	gem install jekyll --no-ri --no-rdoc

RUN     apt-get -y install inotify-tools

COPY etc /etc

VOLUME /root/site /etc/letsencrypt
EXPOSE 80 443
CMD bash -c "if [ ! -e /root/site/_config.yml ]; then jekyll new site; fi; nginx; \
	while true ; do jekyll build --draft -s site -d /usr/share/nginx/html/; inotifywait -r -e create -e modify  /root/site; done"

