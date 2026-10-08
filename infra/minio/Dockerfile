FROM golang:1.24.8-bookworm AS builder

ARG MINIO_VERSION=RELEASE.2025-10-15T17-29-55Z
ARG MC_VERSION=RELEASE.2025-08-13T08-35-41Z

ENV CGO_ENABLED=0 \
    GOBIN=/out

RUN go install github.com/minio/minio@${MINIO_VERSION} \
    && go install github.com/minio/mc@${MC_VERSION}

FROM alpine:3.22.2

RUN apk add --no-cache ca-certificates \
    && addgroup -g 1000 minio \
    && adduser -D -u 1000 -G minio minio \
    && mkdir -p /data \
    && chown minio:minio /data

COPY --from=builder /out/minio /usr/local/bin/minio
COPY --from=builder /out/mc /usr/local/bin/mc

USER minio
EXPOSE 9000 9001

ENTRYPOINT ["/usr/local/bin/minio"]
CMD ["server", "/data", "--console-address", ":9001"]
