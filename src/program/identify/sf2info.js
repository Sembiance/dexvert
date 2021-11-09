/*
import {Program} from "../../Program.js";

export class sf2info extends Program
{
	website = "https://github.com/FluidSynth/fluidsynth";
	gentooPackage = "media-sound/fluidsynth";
	gentooUseFlags = "alsa dbus ipv6 network readline sndfile threads";
	informational = true;
}
*/

/*
"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	website        : "https://github.com/FluidSynth/fluidsynth",
	gentooPackage  : "media-sound/fluidsynth",
	gentooUseFlags : "alsa dbus ipv6 network readline sndfile threads",
	informational  : true
};

exports.bin = () => "fluidsynth";
exports.args = (state, p, r, inPath=state.input.filePath) => (["--audio-driver=file", "--quiet", inPath]);
exports.runOptions = () => ({"ignore-stderr" : true, inputData : "inst 1\nquit"});
exports.post = (state, p, r, cb) =>
{
	const meta = {banks : {}};
	(r.results || "").trim().split("\n").forEach(line =>
	{
		if(!(/^\d/).test(line))
			return;
		
		const props = (line.match(/(?<bank>\d+)-(?<preset>\d+)\s(?<name>.+)$/) || {}).groups;
		if(!props)
			return;
		
		if(!meta.banks[+props.bank])
			meta.banks[+props.bank] = {};
		meta.banks[+props.bank][+props.preset] = props.name;
	});

	Object.assign(r.meta, meta);

	setImmediate(cb);
};
*/
