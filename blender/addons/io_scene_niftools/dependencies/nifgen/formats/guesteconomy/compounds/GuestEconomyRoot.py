from nifgen.formats.guesteconomy.imports import name_type_map
from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct


class GuestEconomyRoot(MemStruct):

	"""
	JWE2: 128 bytes
	#GuestEconomy = {
	#    some parameters might be missing
	#    TargetTicketPrice = 180,
	#a    TargetProfit = 500000,
	#a    TargetDinosaurPrestige = 5000,
	#    TargetSpeciesVariety = 5,
	#    DinosaurPrestigePower = 0.65,
	#    TargetVisitors = 1000,
	#    VisitorArrivalRate = 750,
	#    VisitorDepartureRate = 1000,
	#    IncomeTaxMinIncome = 0,
	#    IncomeTaxMaxIncome = 0,
	#    IncomeTaxMinProportion = 0,
	#    IncomeTaxMaxProportion = 0,
	#    IncomeTaxCurvePower = 1,
	#    TicketPriceVisitorProportionPower = 0.75,
	#    TicketPriceFullVisitorProportion = 1.5,
	
	#    TicketPriceMinimumPriceFraction = 0.4,
	#    VisitorDeathsDecayRate = 2,
	#    VisitorDeathsLimit = 8,
	#    DangerExposureSafeDecayRate = 4,
	#    DangerExposureUnnecessaryShelterPunishment = 1.5,
	#    DangerExposureStormExposurePunishment = 6,
	#    DangerExposureDinosaurExposurePunishment = 8,
	#    DangerExposureDinosaurDangerRadius = 200,
	#    DangerExposureLimit = 8,
	
	#    TransportRatingDisabled = 0
	#},
	# I f I f I 27f
	"""

	__name__ = 'GuestEconomyRoot'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.target_profit = name_type_map['Uint'](self.context, 0, None)
		self.u_00 = name_type_map['Float'](self.context, 0, None)
		self.target_dinosaur_prestige = name_type_map['Uint'](self.context, 0, None)
		self.dinosaur_prestige_power = name_type_map['Float'](self.context, 0, None)
		self.u_01 = name_type_map['Uint'](self.context, 0, None)
		self.u_02 = name_type_map['Float'](self.context, 0, None)
		self.u_03 = name_type_map['Float'](self.context, 0, None)
		self.u_04 = name_type_map['Float'](self.context, 0, None)
		self.visitor_arrival_rate = name_type_map['Float'](self.context, 0, None)
		self.visitor_departure_rate = name_type_map['Float'](self.context, 0, None)
		self.u_05 = name_type_map['Float'](self.context, 0, None)
		self.u_06 = name_type_map['Float'](self.context, 0, None)
		self.u_07 = name_type_map['Float'](self.context, 0, None)
		self.u_08 = name_type_map['Float'](self.context, 0, None)
		self.u_09 = name_type_map['Float'](self.context, 0, None)
		self.u_10 = name_type_map['Float'](self.context, 0, None)
		self.u_11 = name_type_map['Float'](self.context, 0, None)
		self.ticket_price_visitor_proportion_power = name_type_map['Float'](self.context, 0, None)
		self.ticket_price_full_visitor_proportion = name_type_map['Float'](self.context, 0, None)
		self.ticket_price_minimum_price_fraction = name_type_map['Float'](self.context, 0, None)
		self.visitor_deaths_decay_rate = name_type_map['Float'](self.context, 0, None)
		self.visitor_deaths_limit = name_type_map['Float'](self.context, 0, None)
		self.danger_exposure_safe_decay_rate = name_type_map['Float'](self.context, 0, None)
		self.danger_exposure_unnecessary_shelter_punishment = name_type_map['Float'](self.context, 0, None)
		self.danger_exposure_storm_exposure_punishment = name_type_map['Float'](self.context, 0, None)
		self.danger_exposure_dinosaur_exposure_punishment = name_type_map['Float'](self.context, 0, None)
		self.danger_exposure_dinosaur_danger_radius = name_type_map['Float'](self.context, 0, None)
		self.danger_exposure_limit = name_type_map['Float'](self.context, 0, None)
		self.transport_rating_disabled = name_type_map['Uint'](self.context, 0, None)
		self.u_12 = name_type_map['Uint'](self.context, 0, None)
		self.u_13 = name_type_map['Uint'](self.context, 0, None)
		self.u_14 = name_type_map['Uint'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'target_profit', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'u_00', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'target_dinosaur_prestige', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'dinosaur_prestige_power', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'u_01', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'u_02', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'u_03', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'u_04', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'visitor_arrival_rate', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'visitor_departure_rate', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'u_05', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'u_06', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'u_07', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'u_08', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'u_09', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'u_10', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'u_11', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'ticket_price_visitor_proportion_power', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'ticket_price_full_visitor_proportion', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'ticket_price_minimum_price_fraction', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'visitor_deaths_decay_rate', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'visitor_deaths_limit', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'danger_exposure_safe_decay_rate', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'danger_exposure_unnecessary_shelter_punishment', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'danger_exposure_storm_exposure_punishment', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'danger_exposure_dinosaur_exposure_punishment', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'danger_exposure_dinosaur_danger_radius', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'danger_exposure_limit', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'transport_rating_disabled', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'u_12', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'u_13', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'u_14', name_type_map['Uint'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'target_profit', name_type_map['Uint'], (0, None), (False, None)
		yield 'u_00', name_type_map['Float'], (0, None), (False, None)
		yield 'target_dinosaur_prestige', name_type_map['Uint'], (0, None), (False, None)
		yield 'dinosaur_prestige_power', name_type_map['Float'], (0, None), (False, None)
		yield 'u_01', name_type_map['Uint'], (0, None), (False, None)
		yield 'u_02', name_type_map['Float'], (0, None), (False, None)
		yield 'u_03', name_type_map['Float'], (0, None), (False, None)
		yield 'u_04', name_type_map['Float'], (0, None), (False, None)
		yield 'visitor_arrival_rate', name_type_map['Float'], (0, None), (False, None)
		yield 'visitor_departure_rate', name_type_map['Float'], (0, None), (False, None)
		yield 'u_05', name_type_map['Float'], (0, None), (False, None)
		yield 'u_06', name_type_map['Float'], (0, None), (False, None)
		yield 'u_07', name_type_map['Float'], (0, None), (False, None)
		yield 'u_08', name_type_map['Float'], (0, None), (False, None)
		yield 'u_09', name_type_map['Float'], (0, None), (False, None)
		yield 'u_10', name_type_map['Float'], (0, None), (False, None)
		yield 'u_11', name_type_map['Float'], (0, None), (False, None)
		yield 'ticket_price_visitor_proportion_power', name_type_map['Float'], (0, None), (False, None)
		yield 'ticket_price_full_visitor_proportion', name_type_map['Float'], (0, None), (False, None)
		yield 'ticket_price_minimum_price_fraction', name_type_map['Float'], (0, None), (False, None)
		yield 'visitor_deaths_decay_rate', name_type_map['Float'], (0, None), (False, None)
		yield 'visitor_deaths_limit', name_type_map['Float'], (0, None), (False, None)
		yield 'danger_exposure_safe_decay_rate', name_type_map['Float'], (0, None), (False, None)
		yield 'danger_exposure_unnecessary_shelter_punishment', name_type_map['Float'], (0, None), (False, None)
		yield 'danger_exposure_storm_exposure_punishment', name_type_map['Float'], (0, None), (False, None)
		yield 'danger_exposure_dinosaur_exposure_punishment', name_type_map['Float'], (0, None), (False, None)
		yield 'danger_exposure_dinosaur_danger_radius', name_type_map['Float'], (0, None), (False, None)
		yield 'danger_exposure_limit', name_type_map['Float'], (0, None), (False, None)
		yield 'transport_rating_disabled', name_type_map['Uint'], (0, None), (False, None)
		yield 'u_12', name_type_map['Uint'], (0, None), (False, None)
		yield 'u_13', name_type_map['Uint'], (0, None), (False, None)
		yield 'u_14', name_type_map['Uint'], (0, None), (False, None)
