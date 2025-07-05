import {Format} from "../../Format.js";

export class autoCADSlideLibrary extends Format
{
	name       = "AutoCAD Slide Library";
	website    = "http://fileformats.archiveteam.org/wiki/AIN";
	ext        = [".slb"];
	magic      = ["AutoCAD Slide Library", "deark: autocad_slb", /^x-fmt\/104( |$)/];
	idMeta     = ({macFileType, macFileCreator}) => macFileType==="SLB " && macFileCreator==="ACAD";
	notes      = "The sldtoppm utility used to extract these randomly won't extract some images, but then work fine when ran again. This is an issue with sldtoppm as it does this even with a simple bash script.";
	converters = ["unautoCADSlideLibrary", "deark[module:autocad_slb]"];
}
