import {Format} from "../../Format.js";

export class advancedArtStudio extends Format
{
	name          = "Advanced Art Studio";
	website       = "http://fileformats.archiveteam.org/wiki/Advanced_Art_Studio";
	ext           = [".ocp", ".scr", ".win", ".pal"];
	fileSize      = {".ocp" : 10018};
	auxFiles = (input, otherFiles) =>
	{
		const ourExt = input.ext.toLowerCase();

		// .ocp is standalone
		if(ourExt===".ocp")
			return false;
		
		// .scr/.win require a corresponding .pal file
		if([".scr", ".win"].includes(ourExt))
			return otherFiles.filter(otherFile => otherFile.base.toLowerCase()===`${input.name.toLowerCase()}.pal`);
		
		// A .pal requires either a .scr or .win
		return otherFiles.filter(otherFile => [".scr", ".win"].map(ext => input.name.toLowerCase() + ext).includes(otherFile.base.toLowerCase()));
	};

	converters    = ["recoil2png"]

	// TODO need to figure out. maybe untouched?
	//preSteps = [state => { state.processed = state.processed || state.input.ext.toLowerCase()===".pal"; }];
}