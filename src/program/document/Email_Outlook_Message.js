import {Program} from "../../Program.js";

export class Email_Outlook_Message extends Program
{
	website   = "https://metacpan.org/pod/Email::Outlook::Message";
	package   = "app-text/Email-Outlook-Message";
	unsafe    = true;
	bin       = "msgconvert";
	args      = async r => ["--outfile", await r.outFile("out.eml"), r.inFile()];
	renameOut = true;
}
