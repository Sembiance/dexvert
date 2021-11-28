import {Format} from "../../Format.js";

export class graphSaurus extends Format
{
	name     = "Graph Saurus";
	website  = "http://fileformats.archiveteam.org/wiki/Graph_Saurus";
	ext      = [".sr5", ".gl5", ".pl5", ".sr6", ".gl6", ".pl6", ".sr7", ".gl7", ".pl7", ".sr8", ".gl8", ".sri", ".srs"];
	magic    = ["Graph Saurus bitmap", "MSX Graph Saurus"];
	auxFiles = (input, otherFiles) =>
	{
		const ourExt = input.ext.toLowerCase();

		// .pl* must have a corresponding .sr/.gl file
		if(ourExt.startsWith(".pl"))
			return otherFiles.filter(otherFile => [".sr", ".gl"].map(ext => input.name.toLowerCase() + ext + ourExt.charAt(3)).includes(otherFile.base.toLowerCase()));

		// .sr8, .sri and .srs files are standalone
		if([".sr8", ".sri", ".srs"].includes(ourExt))
			return false;
		
		// .gl* or other .sr* file and it'd be nice to have a corresponding .pl* file
		const a = otherFiles.filter(otherFile => otherFile.base.toLowerCase()===`${input.name.toLowerCase()}.pl${ourExt.charAt(3)}`);
		return (a.length>0 ? a : false);
	};

	untouched  = ({f}) => f.input.ext.toLowerCase().startsWith(".pl");
	converters = ["recoil2png"];
}
