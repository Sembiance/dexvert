import {Format} from "../../Format.js";

export class diskCopyImage extends Format
{
	name           = "Apple Disk Copy Image";
	ext            = [".img", ".image", ".bin"];
	forbidExtMatch = true;
	idMeta         = ({macFileType, macFileCreator}) => (["dimg/ddsk", "dImg/dCpy"].includes(`${macFileType}/${macFileCreator}`));
	converters     = ["unar[mac]", "macunpack"];
}
