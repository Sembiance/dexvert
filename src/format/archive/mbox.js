import {Format} from "../../Format.js";

export class mbox extends Format
{
	name           = "Mailbox/MIME Entity";
	website        = "http://fileformats.archiveteam.org/wiki/Mbox";
	ext            = [".mbox"];
	forbidExtMatch = true;
	priority       = this.PRIORITY.LOW;
	magic          = ["Standard Unix Mailbox", "message/rfc822", "application/mbox", "multipart/form-data", "multipart/related;", /^MIME entity/, /^fmt\/950( |$)/, /^Mailbox text/];
	weakMagic      = ["message/rfc822", "application/mbox"];
	converters     = ["ripmime"];	// alternatives: my own "unmbox" munpack (https://manpages.ubuntu.com/manpages/focal/man1/munpack.1.html)   NOTE: (mu extract from package 'mu' doesn't work well, I tried it)
}
