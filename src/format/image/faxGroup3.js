import {Format} from "../../Format.js";

export class faxGroup3 extends Format
{
	name         = "CCITT Fax Group 3";
	website      = "http://fileformats.archiveteam.org/wiki/CCITT_Group_3";
	ext          = [".g3"];
	mimeType     = "image/g3fax";
	metaProvider = ["image"];
	// abydos can also convert this, but it will convert garbage files (text/txt/SKILLS1.G3) and produce garbage, where nconvert/convert are more strict. keyViewPro claims support, but doesn't work
	converters   = ["gimp", "nconvert", "convert"];

	// When it fails, it usually produes a huge/small image (text/txt/SKILLTXT.G3) and authentic ones are almost certain to be smaller than 2500px
	verify = ({meta}) => meta.height>10 && meta.width>10 && meta.width<2500 && meta.height<2500;
}
