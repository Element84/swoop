FROM postgres:15

# May not be ideal, I think it might be upgrading the pg version
# and inflating the image size, but it works for testing.
RUN set -x && \
    apt-get update && \
    apt-get install -y postgresql-15-partman curl make patch && \
    tmp="$(mktemp -d)" && \
    trap "rm -rf '$tmp'" EXIT && \
    cd "$tmp" && \
    curl -L https://github.com/theory/pgtap/archive/refs/tags/v1.2.0.tar.gz -o pgtap.tar.gz && \
    tar -xzf pgtap.tar.gz --strip-components 1 && \
    make install && \
    apt-get remove -y curl make patch && \
    apt-get clean -y && \
    rm -r /var/lib/apt/lists/*
