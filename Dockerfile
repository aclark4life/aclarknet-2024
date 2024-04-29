FROM amazonlinux:2023
RUN dnf install -y shadow-utils python3.11 python3.11-pip make nodejs20-npm nodejs postgresql15 postgresql15-server pango-devel telnet
USER postgres
RUN initdb -D /var/lib/pgsql/data
USER root
RUN useradd wagtail
EXPOSE 8000
ENV PYTHONUNBUFFERED=1 PORT=8000
COPY requirements.txt /
COPY vendor/ /vendor/
RUN python3.11 -m pip install -r /requirements.txt
WORKDIR /app
RUN chown wagtail:wagtail /app
COPY --chown=wagtail:wagtail . .
USER wagtail
RUN cd frontend; npm-20 install; npm-20 run build
RUN python3.11 manage.py collectstatic --noinput --clear
USER postgres
RUN pg_ctl -D /var/lib/pgsql/data -l /tmp/logfile start; 
USER wagtail
CMD set -xe; python3.11 manage.py migrate --noinput; gunicorn backend.wsgi:application
