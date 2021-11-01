"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name          : "MovieSetter Video",
	website       : "http://fileformats.archiveteam.org/wiki/MovieSetter",
	magic         : ["MovieSetter movie", "Amiga Moviesetter animation", "MovieSetter project"],
	notes         : "Xanim doesn't play sound and couldn't find another linux based converter that supports sound. Only known solution now would be to convert it on a virtual amiga with MovieSetter itself probably. CYC and demo_5 don't convert.",
	keepFilename  : true,
	filesOptional : (state, otherFiles, otherDirs) => ([...otherFiles, ...otherDirs])																																								// MovieSetter videos can reference external files, so include symlinks to everything else
};

exports.converterPriority = ["xanim"];
