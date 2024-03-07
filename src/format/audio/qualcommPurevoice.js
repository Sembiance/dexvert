import {Format} from "../../Format.js";

export class qualcommPurevoice extends Format
{
	name         = "Qualcomm Purevoice Audio";
	website      = "http://fileformats.archiveteam.org/wiki/Qualcomm_QCP";
	ext          = [".qcp"];
	magic        = ["QualComm PureVoice", "RIFF Datei: unbekannter Typ 'QLCM'", /^fmt\/962( |$)/];
	converters   = ["PVConverter"];
}
