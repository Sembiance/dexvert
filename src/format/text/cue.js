"use strict";
const XU = require("@sembiance/xu"),
	cueParser = require("cue-parser");

exports.meta =
{
	name    : "ISO CUE Sheet",
	website : "http://fileformats.archiveteam.org/wiki/CUE_and_BIN",
	ext     : [".cue"],
	magic   : ["ISO CDImage cue", "Cue Sheet"]
};

exports.inputMeta = (state, p, cb) =>
{
	const cueData = cueParser.parse(state.input.absolute);
	if(!cueData || !cueData.files || cueData.files.length===0)
		return;
	
	state.input.meta.cue = JSON.parse(JSON.stringify(cueData));
	Object.keys(state.input.meta.cue).forEach(k =>
	{
		if(state.input.meta.cue[k]===null)
			delete state.input.meta.cue[k];
	});

	Object.keys(state.input.meta.cue.track || {}).forEach(k =>
	{
		if(state.input.meta.cue.track[k]===null)
			delete state.input.meta.cue.track[k];
	});

	state.input.meta.cue.files.flatMap(file => file.tracks || []).forEach(track =>
	{
		Object.keys(track).forEach(k =>
		{
			if(track[k]===null)
				delete track[k];
		});
	});

	state.processed = true;

	p.family.supportedInputMeta(state, p, cb);
};
