import {Format} from "../../Format.js";

export class faxGroup3 extends Format
{
	name         = "CCITT Fax Group 3";
	website      = "http://fileformats.archiveteam.org/wiki/CCITT_Group_3";
	ext          = [".g3"];
	mimeType     = "image/g3fax";
	metaProvider = ["image"];
	// So all we have is an extension match and garbage .g3 files will convert into garabge sadly. abydosconvert can also convert these but is a bit more loosey goosey. keyViewPro claims support, but doesn't work
	// There isn't anything else I've found that I can do about it though, we're already checking meta and classifying it for garbage
	converters   = ["gimp", "nconvert", "convert"];
	classify     = true;

	// When it fails, it usually produes a huge/small image (text/txt/SKILLTXT.G3) and authentic ones are almost certain to be smaller than 2500px
	verify = ({meta}) => meta.height>10 && meta.width>10 && meta.width<2500 && meta.height<2500;
}
