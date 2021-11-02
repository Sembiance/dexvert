import {Format} from "../../Format.js";

export class mur extends Format
{
	name          = "C.O.L.R. Object Editor";
	website       = "http://fileformats.archiveteam.org/wiki/C.O.L.R._Object_Editor";
	ext           = [".mur", ".pal"];
	// Both .mur and .pal are required
	auxFiles = (input, otherFiles) => otherFiles.filter(file => file.base.toLowerCase()===(input.name.toLowerCase() + this.ext.find(ext => ext!==input.ext.toLowerCase())));
	
	converters    = ["recoil2png"]

	// TODO Need to figure out a way to mark the .pal file as processed and don't bother with conversion
	//preSteps = [state => { state.processed = state.processed || state.input.ext.toLowerCase()===".pal"; }];
}
