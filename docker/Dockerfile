FROM ubuntu:focal

RUN apt-get update && \
	DEBIAN_FRONTEND=noninteractive apt-get -y install software-properties-common && \
	DEBIAN_FRONTEND=noninteractive apt-get -y install \
		build-essential \
		cmake \
		git \
		openssl \
		libssl-dev \
		python3 \
		python3-pip \
		libncurses5 \
		python3.8-venv \
		python3-virtualenv \
		autoconf \
		automake \
		libtool \
		pkg-config \
		m4 \
		wget \
		zlib1g-dev \
		upx \
		doxygen \
		graphviz \
		gcc-multilib \
		ninja-build \
		zip && \
	apt-get clean && \
	apt-get auto-remove -y && \
	rm -rf /var/cache/apt/* && \
	rm -rf /var/lib/apt/lists/* && \
	rm -rf /tmp/*

RUN wget http://releases.llvm.org/3.9.1/clang+llvm-3.9.1-x86_64-linux-gnu-ubuntu-16.04.tar.xz && \
	tar xf clang+llvm-3.9.1-x86_64-linux-gnu-ubuntu-16.04.tar.xz && \
	mv clang+llvm-3.9.1-x86_64-linux-gnu-ubuntu-16.04 clang && \
	rm clang+llvm-3.9.1-x86_64-linux-gnu-ubuntu-16.04.tar.xz

RUN ln -s /usr/lib/libncurses.so.5 /usr/lib/libtinfo.so.5
