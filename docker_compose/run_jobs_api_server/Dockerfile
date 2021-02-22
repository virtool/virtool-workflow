FROM library/python:3.8-buster as server
WORKDIR /build
RUN python -m pip install --upgrade pip
RUN git clone --single-branch --branch release/5.0.0 https://github.com/virtool/virtool/
RUN sed "s/idna==3.1/idna==2.10/g" ./virtool/requirements.txt > ./virtool/modified-requirements.txt
RUN pip install --user -r ./virtool/modified-requirements.txt


FROM virtool/external-tools:0.2.0
# Copy python packages installed by pip
COPY --from=server /root/.local /root/.local
COPY --from=server /build/virtool/virtool /virtool/virtool
COPY --from=server /build/virtool/run.py /virtool/run.py

WORKDIR /virtool

EXPOSE 9950
ENTRYPOINT ["python", "run.py"]
CMD ["jobsAPI"]