import {Format} from "../../Format.js";

export class corelPhotoPaint extends Format
{
	name       = "Corel Photo-Paint Image";
	website    = "http://fileformats.archiveteam.org/wiki/Corel_Photo-Paint_image";
	ext        = [".cpt"];
	magic      = ["Corel Photo Paint bitmap", "Corel Photo-Paint image", /^x-fmt\/144( |$)/];
	idMeta     = ({macFileType, macFileCreator}) => ["CPT8", "CPT7"].includes(macFileType) && macFileCreator==="Cpnt";
	converters = ["vibe2png"];
}
