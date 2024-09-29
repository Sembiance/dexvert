import {Format} from "../../Format.js";

export class printShopGSGraphic extends Format
{
	name        = "Print Shop GS Graphic";
	fileSize    = 1716;
	idMeta      = ({proDOSType, proDOSTypeAux}) => proDOSType==="F8" && proDOSTypeAux==="C323";
	converters  = ["deark[module:printshop_gs]"];
}
