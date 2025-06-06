import {Format} from "../../Format.js";

export class scitexCT extends Format
{
	name           = "Scitex Continuous Tone";
	website        = "http://fileformats.archiveteam.org/wiki/Scitex_CT";
	ext            = [".ct", ".sct"];
	forbidExtMatch = true;
	magic          = ["Scitex Continuous Tone bitmap", "SciTex :sct:", /^x-fmt\/146( |$)/];
	idMeta         = ({macFileType, macFileCreator}) => macFileType==="..CT" && macFileCreator==="8BIM";
	converters     = ["nconvert[format:sct]", "corelPhotoPaint[outType:tiff][strongMatch]", "corelDRAW[strongMatch]"];
	verify         = ({meta}) => !Object.hasOwn(meta, "colorCount") || meta.colorCount>1;	// colorCount isn't present on larger images (tsuperbridge.sct.cmyk) so we only enforce color checks on smaller images that are not really scitexCT
}
