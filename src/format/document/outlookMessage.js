import {Format} from "../../Format.js";

export class outlookMessage extends Format
{
	name           = "Outlook Message";
	website        = "http://fileformats.archiveteam.org/wiki/Outlook_Item_File";
	ext            = [".msg"];
	forbidExtMatch = true;
	magic          = ["CDFV2 Microsoft Outlook Message", "Outlook Message", /^x-fmt\/430( |$)/];
	converters     = ["Email_Outlook_Message"];
}
