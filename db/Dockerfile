FROM postgres:15

# May not be ideal, I think it might be upgrading the pg version
# and inflating the image size, but it works for testing.

# install build deps and pg_partman
RUN set -x && \
    apt-get update && \
    apt-get install -y postgresql-15-partman curl make patch perl && \
    apt-get clean -y && \
    rm -r /var/lib/apt/lists/*

# install pg_prove
RUN cpan TAP::Parser::SourceHandler::pgTAP


# install dbmate and wrapper
COPY dbmate /usr/local/bin/dbmate
RUN set -x && \
    DBMATE="/usr/local/bin/_dbmate" && \
    ARCH="$(a="$(uname -m)"; [ "$a" = "aarch64" ] && echo "arm64" || [ "$a" = "x86_64" ] && echo "amd64" || echo "$a")" && \
    curl -fsSL -o "$DBMATE" https://github.com/amacneil/dbmate/releases/download/v2.2.0/dbmate-linux-$ARCH && \
    chmod +x "$DBMATE"

# install pgtap
RUN set -x && \
    tmp="$(mktemp -d)" && \
    trap "rm -rf '$tmp'" EXIT && \
    cd "$tmp" && \
    curl -fsSL https://github.com/theory/pgtap/archive/refs/tags/v1.2.0.tar.gz -o pgtap.tar.gz && \
    tar -xzf pgtap.tar.gz --strip-components 1 && \
    make install
