import {xu} from "xu";
import {Format} from "../../Format.js";

export class mayaScene extends Format
{
	name        = "Maya Scene";
	website     = "http://fileformats.archiveteam.org/wiki/Maya_scene";
	ext         = [".mb", ".ma"];
	magic       = ["Maya Binary Scene", "Alias Maya Binary File", "Alias Maya Ascii File", "Maya ASCII Scene", /^fmt\/(861|862|863)( |$)/];
	unsupported = true;
	notes       = xu.trim`
		So the discmaster site only has like 64 unique maya files.
		Maya 5 would only open 1 of my sample files, the others being newer than that.
		Assimp claims some ASCII version support, but didn't handle any of my samples. MilkShape3D also says limited support for ASCII, but it crashed on all my samples.
		It's also a massive pain to get Maya running and due to the tiny number of files in the wild, just not worth supporting right now.`;
}
