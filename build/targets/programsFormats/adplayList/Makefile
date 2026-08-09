# Vibe coded by Codex

CXX ?= g++
CXXFLAGS ?= -O2 -Wall -Wextra
CPPFLAGS += $(shell pkg-config --cflags adplug)
LDLIBS += $(shell pkg-config --libs adplug)

adplayList: adplayList.cpp
	$(CXX) $(CPPFLAGS) $(CXXFLAGS) $< $(LDLIBS) -o $@

.PHONY: clean
clean:
	$(RM) adplayList
