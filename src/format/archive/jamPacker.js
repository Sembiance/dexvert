import {Format} from "../../Format.js";

export class jamPacker extends Format
{
	name       = "JAM Packer Compressed File";
	website    = "http://fileformats.archiveteam.org/wiki/The_JAM_Packer";
	ext        = [".jpk"];
	magic      = ["JAM Packer compressed data", "JAM Packer compressed disk image", "LZH: JAMPacker", "LSD: JAMPacker", "LZW: JAMPacker LZW", /^JEK: Jek Packer.*JAM Packer/];
	packed     = true;
	converters = ["xfdDecrunch", "ancient"];
}
