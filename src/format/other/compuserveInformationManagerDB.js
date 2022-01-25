import {Format} from "../../Format.js";

export class compuserveInformationManagerDB extends Format
{
	name       = "Compuserve Information Manager DB";
	magic      = ["CompuServe Information Manager DB"];
	converters = ["strings"];
}
