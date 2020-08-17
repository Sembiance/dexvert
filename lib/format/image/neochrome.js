"use strict";
const XU = require("@sembiance/xu"),
	fs = require("fs");

exports.meta =
{
	name     : "Neochrome",
	website  : "http://fileformats.archiveteam.org/wiki/NEOchrome",
	ext      : [".neo", ".rst"],
	mimeType : "image/x-neo",
	filesize : [state =>
	{
		const ext = state.input.ext.toLowerCase();
		if([".rst"].includes(ext))
			return fs.statSync(state.input.absolute).size;

		return 32128;
	}],
	// .neo can convert on it's own but optionally uses a .rst which is useless on it's own without a corresponding .neo
	filesRequired : (state, otherFiles) => (state.input.ext.toLowerCase()===".neo" ? false : otherFiles.filter(otherFile => otherFile.toLowerCase()===`${state.input.name.toLowerCase()}.neo`)),
	filesOptional : (state, otherFiles) => (state.input.ext.toLowerCase()===".rst" ? false : otherFiles.filter(otherFile => otherFile.toLowerCase()===`${state.input.name.toLowerCase()}.rst`))
};

exports.preSteps = [state => { state.processed = state.processed || state.input.ext.toLowerCase()===".rst"; }];

exports.converterPriorty = ["recoil2png", "nconvert", "abydosconvert"];
