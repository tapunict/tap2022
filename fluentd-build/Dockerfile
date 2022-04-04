FROM fluent/fluentd:edge-debian
USER root

RUN apt-get update && apt-get -y install build-essential 
RUN gem uninstall -i /usr/local/bundle -aIx
RUN gem uninstall -i /usr/local/lib/ruby/gems/2.7.0 -aIx
RUN gem uninstall -aIx
RUN gem install  http_parser.rb:0.6.0 eventmachine fluent-plugin-twitter


# to build with
# docker build . --tag tap:fluentweet
# and run with 
# docker run -v $(pwd)/conf:/fluentd/etc tap:fluentweet -c /fluentd/etc/twitter.conf
