import {Format} from "../../Format.js";

export class adobeType1 extends Format
{
	name         = "Adobe Type 1 Font";
	website      = "http://fileformats.archiveteam.org/wiki/Adobe_Type_1";
	ext          = [".pfa", ".pfb"];
	magic        = ["Adobe Type 1 Font", "Adobe PostScript Type 1 Font", "PostScript Type 1 font", "Adobe Printer Font Binary", "application/x-font-type1", /^fmt\/525( |$)/];
	idMeta       = ({macFileType, macFileCreator}) => macFileType==="LWFN" && ["ACP1", "ACp1", "ACP3", "ASPF", "EMGR", "LWRT"].includes(macFileCreator);
	metaProvider = ["fc_scan"];
	converters   = ["fontforge[matchType:magic]"];
}
