import {xu} from "xu";
import {Format} from "../../Format.js";

const _IMF_MAGIC = ["E-Mail message", "news or mail", "news, ASCII text", "SMTP mail text", "SMTP mail,", "RFC 822 mail"];
export {_IMF_MAGIC};

export class imf extends Format
{
	name           = "Internet Message Format";
	website        = "http://fileformats.archiveteam.org/wiki/Internet_e-mail_message_format";
	ext            = [".eml", ".msg"];
	forbidExtMatch = true;
	magic          = _IMF_MAGIC;
	untouched      = true;
	notes          = xu.trim`
		With several RFC files describing the format, you'd think this would be straight forward to parse, but it's a total nightmare.
		I had spent some time looking for a good program to parse it, and failed.
		I spent more time trying to code my own that would output JSON, but there are just a ton of edge cases and I gave up.
		In addition to the website link above, more details here: https://mailformat.dan.info/
		Once I get working, update program Email_Outlook_Message to chain to convert the resulting .eml into this format handler (to handle attachments). Then re-process document/outlookMessage CDs`;
}
