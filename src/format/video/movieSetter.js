import {xu} from "xu";
import {Format} from "../../Format.js";

export class movieSetter extends Format
{
	name         = "MovieSetter Video";
	website      = "http://fileformats.archiveteam.org/wiki/MovieSetter";
	magic        = ["MovieSetter movie", "Amiga Moviesetter animation", "MovieSetter project"];
	notes        = xu.trim`
		Xanim doesn't play sound and couldn't find another linux based converter that supports sound. Only known solution now would be to convert it on a virtual amiga with MovieSetter itself probably. CYC and demo_5 don't convert.
		Also exists is video/movieSetterSet which is currently unsupported, don't know what can convert it.`;
	keepFilename = true;
	auxFiles     = (input, otherFiles, otherDirs) => ((otherFiles.length>0 || otherDirs.length>0) ? [...otherFiles, ...otherDirs] : false);
	converters   = ["xanim"];
}
