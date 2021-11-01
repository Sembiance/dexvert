"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Graph Saurus",
	website  : "http://fileformats.archiveteam.org/wiki/Graph_Saurus",
	ext      : [".sr5", ".gl5", ".pl5", ".sr6", ".gl6", ".pl6", ".sr7", ".gl7", ".pl7", ".sr8", ".gl8", ".sri", ".srs"],
	magic    : ["Graph Saurus bitmap", "MSX Graph Saurus"],
	filesRequired : (state, otherFiles) =>
	{
		const ourExt = state.input.ext.toLowerCase();

		// .sr* and .gl* files don't REQUIRE any other files, just nice to have
		if(ourExt.startsWith(".sr") || ourExt.startsWith(".gl"))
			return false;

		// Otherwise we are a .pl* then we must have a corresponding .sr/.gl file
		return otherFiles.filter(otherFile => [".sr", ".gl"].map(ext => state.input.name.toLowerCase() + ext + ourExt.charAt(3)).includes(otherFile.toLowerCase()));
	},
	filesOptional : (state, otherFiles) =>
	{
		const ourExt = state.input.ext.toLowerCase();

		// .sr8, .sri and .srs files are standalone and .pl files are handled by the above
		if([".sr8", ".sri", ".srs"].includes(ourExt) || ourExt.startsWith(".pl"))
			return false;

		// Otherwise we are a .gl* or other .sr* file and it'd be nice to have a corresponding .pl* file
		return otherFiles.filter(otherFile => otherFile.toLowerCase()===`${state.input.name.toLowerCase()}.pl${ourExt.charAt(3)}`);
	}
};

exports.preSteps = [state => { state.processed = state.processed || state.input.ext.toLowerCase().startsWith(".pl"); }];

exports.converterPriority = ["recoil2png"];
