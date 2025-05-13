import {xu} from "xu";
import {Format} from "../../Format.js";

export class pageMaker extends Format
{
	name           = "Aldus/Adobe PageMaker";
	website        = "http://fileformats.archiveteam.org/wiki/PageMaker";
	ext            = [".pmd", ".pmt", ".pm3", ".pm4", ".pm5", ".pm6", ".p65"];
	forbidExtMatch = true;
	magic          = ["Aldus PageMaker document", "Adobe PageMaker document", "Page Maker 7 Document", /^x-fmt\/(173|174|181|352)( |$)/, /^fmt\/(876|1686|1687|1718|1719)( |$)/];
	idMeta         = ({macFileType, macFileCreator}) => ["AB65", "ALB4", "ALB5", "ALB6", "ALT4", "ALT5", "ALT6", "AT65"].includes(macFileType) && ["AD65", "ALD4", "ALD5", "ALD6"].includes(macFileCreator);
	converters     = ["soffice[format:PageMakerDocument]", "pageMaker7", "pageMaker5", "pageMaker4"];	// Don't be tempted to prioritize pageMaker4 or pageMaker5 for version 4/5 documents, as PageMaker7 when it can open them prints them better
}
