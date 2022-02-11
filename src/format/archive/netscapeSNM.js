import {Format} from "../../Format.js";

export class netscapeSNM extends Format
{
	name        = "Netscape SNM Archive";
	ext         = [".snm"];
	magic       = ["Netscape folder cache", "Netscape Mail Message"];
	notes       = "Could convert with: https://github.com/lantaoxu/Windows-Server-2003/blob/5c6fe3db626b63a384230a1aa6b92ac416b0765f/inetcore/outlookexpress/import/netscape/commimp.cpp";
	unsupported = true;
}
