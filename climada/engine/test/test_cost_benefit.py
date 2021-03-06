"""
This file is part of CLIMADA.

Copyright (C) 2017 ETH Zurich, CLIMADA contributors listed in AUTHORS.

CLIMADA is free software: you can redistribute it and/or modify it under the
terms of the GNU Lesser General Public License as published by the Free
Software Foundation, version 3.

CLIMADA is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License along
with CLIMADA. If not, see <https://www.gnu.org/licenses/>.

---

Test CostBenefit class.
"""
import os
import copy
import unittest
import numpy as np

from climada.entity.entity_def import Entity
from climada.entity.disc_rates import DiscRates
from climada.hazard.base import Hazard
from climada.engine.cost_benefit import CostBenefit, risk_aai_agg, DEF_RP, \
risk_rp_100, risk_rp_250
from climada.engine import Impact
from climada.util.constants import ENT_DEMO_FUTURE, ENT_DEMO_TODAY

HAZ_DATA_DIR = os.path.join(os.path.dirname(__file__), '../../hazard/test/data')
HAZ_TEST_MAT = os.path.join(HAZ_DATA_DIR, 'atl_prob_no_name.mat')
ENT_TEST_MAT = os.path.join(os.path.dirname(__file__),
                            '../../entity/exposures/test/data/demo_today.mat')

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')

class TestSteps(unittest.TestCase):
    '''Test intermediate steps'''
    def test_calc_impact_measures_pass(self):
        """Test _calc_impact_measures against reference value"""

        hazard = Hazard('TC')
        hazard.read_mat(HAZ_TEST_MAT)
        entity = Entity()
        entity.read_mat(ENT_TEST_MAT)
        entity.check()
        entity.measures._data['TC'] = entity.measures._data.pop('XX')
        for meas in entity.measures.get_measure('TC'):
            meas.haz_type = 'TC'
        entity.check()

        cost_ben = CostBenefit()
        cost_ben._calc_impact_measures(hazard, entity.exposures, entity.measures,
            entity.impact_funcs, when='future', risk_func=risk_aai_agg, save_imp=True)

        self.assertEqual(cost_ben.imp_meas_present, dict())
        self.assertEqual(cost_ben.cost_ben_ratio, dict())
        self.assertEqual(cost_ben.benefit, dict())
        self.assertEqual(cost_ben.tot_climate_risk, 0.0)
        self.assertEqual(cost_ben.present_year, 2016)
        self.assertEqual(cost_ben.future_year, 2030)

        self.assertEqual(cost_ben.imp_meas_future['no measure']['cost'], 0)
        self.assertEqual(cost_ben.imp_meas_future['no measure']['risk'], 6.51220115756442e+09)
        self.assertTrue(np.array_equal(cost_ben.imp_meas_future['no measure']['efc'].return_per, DEF_RP))
        self.assertEqual(cost_ben.imp_meas_future['no measure']['impact'].at_event.nonzero()[0].size, 841)
        self.assertEqual(cost_ben.imp_meas_future['no measure']['impact'].at_event[14082], 8.801682862431524e+06)
        self.assertEqual(cost_ben.imp_meas_future['no measure']['impact'].tot_value, 6.570532945599105e+11)
        self.assertEqual(cost_ben.imp_meas_future['no measure']['impact'].aai_agg, 6.51220115756442e+09)

        self.assertEqual(cost_ben.imp_meas_future['Mangroves']['cost'], 1.3117683608515418e+09)
        self.assertEqual(cost_ben.imp_meas_future['Mangroves']['risk'], 4.850407096284983e+09)
        self.assertEqual(cost_ben.imp_meas_future['Mangroves']['efc'].impact[1], 9.566015222449379e+08)
        self.assertTrue(np.array_equal(cost_ben.imp_meas_future['Mangroves']['efc'].return_per, DEF_RP))
        self.assertEqual(cost_ben.imp_meas_future['Mangroves']['impact'].at_event.nonzero()[0].size, 665)
        self.assertEqual(cost_ben.imp_meas_future['Mangroves']['impact'].at_event[13901], 1.29576562770977e+09)
        self.assertEqual(cost_ben.imp_meas_future['Mangroves']['impact'].tot_value, 6.570532945599105e+11)
        self.assertEqual(cost_ben.imp_meas_future['Mangroves']['impact'].aai_agg, 4.850407096284983e+09)

        self.assertEqual(cost_ben.imp_meas_future['Beach nourishment']['cost'], 1.728000000000000e+09)
        self.assertEqual(cost_ben.imp_meas_future['Beach nourishment']['risk'], 5.188921355413834e+09)
        self.assertEqual(cost_ben.imp_meas_future['Beach nourishment']['efc'].impact[2], 8.406917562074616e+09)
        self.assertTrue(np.array_equal(cost_ben.imp_meas_future['Beach nourishment']['efc'].return_per, DEF_RP))
        self.assertEqual(cost_ben.imp_meas_future['Beach nourishment']['impact'].at_event.nonzero()[0].size, 702)
        self.assertEqual(cost_ben.imp_meas_future['Beach nourishment']['impact'].at_event[1110], 0.0)
        self.assertEqual(cost_ben.imp_meas_future['Beach nourishment']['impact'].eai_exp[5], 1.1133679079730146e+08)
        self.assertEqual(cost_ben.imp_meas_future['Beach nourishment']['impact'].tot_value, 6.570532945599105e+11)
        self.assertEqual(cost_ben.imp_meas_future['Beach nourishment']['impact'].aai_agg, 5.188921355413834e+09)

        self.assertEqual(cost_ben.imp_meas_future['Seawall']['cost'], 8.878779433630093e+09)
        self.assertEqual(cost_ben.imp_meas_future['Seawall']['risk'], 4.736400526119911e+09)
        self.assertTrue(np.array_equal(cost_ben.imp_meas_future['Seawall']['efc'].return_per, DEF_RP))
        self.assertEqual(cost_ben.imp_meas_future['Seawall']['impact'].at_event.nonzero()[0].size, 73)
        self.assertEqual(cost_ben.imp_meas_future['Seawall']['impact'].at_event[1229], 0.0)
        self.assertEqual(cost_ben.imp_meas_future['Seawall']['impact'].tot_value, 6.570532945599105e+11)
        self.assertEqual(cost_ben.imp_meas_future['Seawall']['impact'].aai_agg, 4.736400526119911e+09)

        self.assertEqual(cost_ben.imp_meas_future['Building code']['cost'], 9.200000000000000e+09)
        self.assertEqual(cost_ben.imp_meas_future['Building code']['risk'], 4.884150868173321e+09)
        self.assertEqual(cost_ben.imp_meas_future['Building code']['efc'].impact[1], 1.4311415248995776e+09)
        self.assertTrue(np.array_equal(cost_ben.imp_meas_future['Building code']['efc'].return_per, DEF_RP))
        self.assertEqual(cost_ben.imp_meas_future['Building code']['impact'].at_event.nonzero()[0].size, 841)
        self.assertEqual(cost_ben.imp_meas_future['Building code']['impact'].at_event[122], 0.0)
        self.assertEqual(cost_ben.imp_meas_future['Building code']['impact'].eai_exp[11], 7.757060129393841e+07)
        self.assertEqual(cost_ben.imp_meas_future['Building code']['impact'].tot_value, 6.570532945599105e+11)
        self.assertEqual(cost_ben.imp_meas_future['Building code']['impact'].aai_agg, 4.884150868173321e+09)

    def test_calc_cb_no_change_pass(self):
        """Test _calc_cost_benefit without present value against reference value"""
        hazard = Hazard('TC')
        hazard.read_mat(HAZ_TEST_MAT)
        entity = Entity()
        entity.read_mat(ENT_TEST_MAT)
        entity.measures._data['TC'] = entity.measures._data.pop('XX')
        for meas in entity.measures.get_measure('TC'):
            meas.haz_type = 'TC'
        entity.check()

        cost_ben = CostBenefit()
        cost_ben._calc_impact_measures(hazard, entity.exposures, entity.measures,
            entity.impact_funcs, when='future', risk_func=risk_aai_agg, save_imp=True)

        cost_ben.present_year = 2018
        cost_ben.future_year = 2040
        cost_ben._calc_cost_benefit(entity.disc_rates)

        self.assertEqual(cost_ben.imp_meas_present, dict())
        self.assertEqual(len(cost_ben.imp_meas_future), 5)
        self.assertEqual(cost_ben.present_year, 2018)
        self.assertEqual(cost_ben.future_year, 2040)

        self.assertEqual(cost_ben.cost_ben_ratio['Mangroves'], 0.04230714690616641)
        self.assertEqual(cost_ben.cost_ben_ratio['Beach nourishment'], 0.06998836431681373)
        self.assertEqual(cost_ben.cost_ben_ratio['Seawall'], 0.2679741183248266)
        self.assertEqual(cost_ben.cost_ben_ratio['Building code'], 0.30286828677985717)

        self.assertEqual(cost_ben.benefit['Mangroves'], 3.100583368954022e+10)
        self.assertEqual(cost_ben.benefit['Beach nourishment'], 2.468981832719974e+10)
        self.assertEqual(cost_ben.benefit['Seawall'], 3.3132973770502796e+10)
        self.assertEqual(cost_ben.benefit['Building code'], 3.0376240767284798e+10)

        self.assertEqual(cost_ben.tot_climate_risk, 1.2150496306913972e+11)

    def test_calc_cb_change_pass(self):
        """Test _calc_cost_benefit with present value against reference value"""
        hazard = Hazard('TC')
        hazard.read_mat(HAZ_TEST_MAT)
        entity = Entity()
        entity.read_mat(ENT_TEST_MAT)
        entity.measures._data['TC'] = entity.measures._data.pop('XX')
        for meas in entity.measures.get_measure('TC'):
            meas.haz_type = 'TC'
        entity.check()

        cost_ben = CostBenefit()
        cost_ben._calc_impact_measures(hazard, entity.exposures, entity.measures,
            entity.impact_funcs, when='present', risk_func=risk_aai_agg, save_imp=False)

        ent_future = Entity()
        ent_future.read_excel(ENT_DEMO_FUTURE)
        ent_future.check()

        haz_future = copy.deepcopy(hazard)
        haz_future.intensity.data += 25

        cost_ben._calc_impact_measures(haz_future, ent_future.exposures, ent_future.measures,
            ent_future.impact_funcs, when='future', risk_func=risk_aai_agg, save_imp=False)

        cost_ben.present_year = 2018
        cost_ben.future_year = 2040
        cost_ben._calc_cost_benefit(entity.disc_rates, imp_time_depen=1)

        self.assertEqual(cost_ben.present_year, 2018)
        self.assertEqual(cost_ben.future_year, 2040)
        self.assertEqual(cost_ben.tot_climate_risk, 5.768659152882021e+11)

        self.assertEqual(cost_ben.imp_meas_present['no measure']['risk'], 6.51220115756442e+09)
        self.assertEqual(cost_ben.imp_meas_present['Mangroves']['risk'], 4.850407096284983e+09)
        self.assertEqual(cost_ben.imp_meas_present['Beach nourishment']['risk'], 5.188921355413834e+09)
        self.assertEqual(cost_ben.imp_meas_present['Seawall']['risk'], 4.736400526119911e+09)
        self.assertEqual(cost_ben.imp_meas_present['Building code']['risk'], 4.884150868173321e+09)

        self.assertEqual(cost_ben.imp_meas_future['no measure']['risk'], 5.9506659786664024e+10)
        self.assertEqual(cost_ben.imp_meas_future['Mangroves']['risk'], 4.826231151473135e+10)
        self.assertEqual(cost_ben.imp_meas_future['Beach nourishment']['risk'], 5.0647250923231674e+10)
        self.assertEqual(cost_ben.imp_meas_future['Seawall']['risk'], 21089567135.7345)
        self.assertEqual(cost_ben.imp_meas_future['Building code']['risk'], 4.462999483999791e+10)

    def test_time_array_pres_pass(self):
        """ Test _time_dependency_array """
        cb = CostBenefit()
        cb.present_year = 2018
        cb.future_year = 2030
        imp_time_depen = 1.0
        time_arr = cb._time_dependency_array(imp_time_depen)

        n_years = cb.future_year - cb.present_year + 1
        self.assertEqual(time_arr.size, n_years)
        self.assertTrue(np.allclose(time_arr[:-1], np.arange(0, 1, 1/(n_years-1))))
        self.assertEqual(time_arr[-1], 1)

        imp_time_depen = 0.5
        time_arr = cb._time_dependency_array(imp_time_depen)

        n_years = cb.future_year - cb.present_year + 1
        self.assertEqual(time_arr.size, n_years)
        self.assertTrue(np.allclose(time_arr, np.arange(n_years)**imp_time_depen / \
                (n_years-1)**imp_time_depen))

    def test_time_array_no_pres_pass(self):
        """ Test _time_dependency_array """
        cb = CostBenefit()
        cb.present_year = 2018
        cb.future_year = 2030
        time_arr = cb._time_dependency_array()

        n_years = cb.future_year - cb.present_year + 1
        self.assertEqual(time_arr.size, n_years)
        self.assertTrue(np.array_equal(time_arr, np.ones(n_years)))

    def test_npv_unaverted_no_pres_pass(self):
        """ Test _npv_unaverted_impact """
        cb = CostBenefit()
        cb.present_year = 2018
        cb.future_year = 2030
        risk_future = 1000
        disc_rates = DiscRates()
        disc_rates.years = np.arange(cb.present_year, cb.future_year+1)
        disc_rates.rates = np.ones(disc_rates.years.size)*0.025
        time_dep = np.linspace(0, 1, disc_rates.years.size)
        res = cb._npv_unaverted_impact(risk_future, disc_rates, time_dep,
                              risk_present=None)

        self.assertEqual(res, disc_rates.net_present_value(cb.present_year, \
                cb.future_year, time_dep * risk_future))

    def test_npv_unaverted_pres_pass(self):
        """ Test _npv_unaverted_impact """
        cb = CostBenefit()
        cb.present_year = 2018
        cb.future_year = 2030
        risk_future = 1000
        risk_present = 500
        disc_rates = DiscRates()
        disc_rates.years = np.arange(cb.present_year, cb.future_year+1)
        disc_rates.rates = np.ones(disc_rates.years.size)*0.025
        time_dep = np.linspace(0, 1, disc_rates.years.size)
        res = cb._npv_unaverted_impact(risk_future, disc_rates, time_dep,
                              risk_present)


        tot_climate_risk = risk_present + (risk_future-risk_present) * time_dep
        self.assertEqual(res, disc_rates.net_present_value(cb.present_year, \
            cb.future_year, tot_climate_risk))

    def test_norm_value(self):
        """ Test _norm_values """
        cb = CostBenefit()
        norm_fact, norm_name = cb._norm_values(1)
        self.assertEqual(norm_fact, 1)
        self.assertEqual(norm_name, "")

        norm_fact, norm_name = cb._norm_values(10)
        self.assertEqual(norm_fact, 1)
        self.assertEqual(norm_name, "")

        norm_fact, norm_name = cb._norm_values(100)
        self.assertEqual(norm_fact, 1)
        self.assertEqual(norm_name, "")

        norm_fact, norm_name = cb._norm_values(1001)
        self.assertEqual(norm_fact, 1000)
        self.assertEqual(norm_name, "k")

        norm_fact, norm_name = cb._norm_values(10000)
        self.assertEqual(norm_fact, 1000)
        self.assertEqual(norm_name, "k")

        norm_fact, norm_name = cb._norm_values(1.01e6)
        self.assertEqual(norm_fact, 1.0e6)
        self.assertEqual(norm_name, "m")

        norm_fact, norm_name = cb._norm_values(1.0e8)
        self.assertEqual(norm_fact, 1.0e6)
        self.assertEqual(norm_name, "m")

        norm_fact, norm_name = cb._norm_values(1.01e9)
        self.assertEqual(norm_fact, 1.0e9)
        self.assertEqual(norm_name, "bn")

        norm_fact, norm_name = cb._norm_values(1.0e10)
        self.assertEqual(norm_fact, 1.0e9)
        self.assertEqual(norm_name, "bn")

        norm_fact, norm_name = cb._norm_values(1.0e12)
        self.assertEqual(norm_fact, 1.0e9)
        self.assertEqual(norm_name, "bn")

class TestCalc(unittest.TestCase):
    '''Test calc'''

    def test_calc_change_pass(self):
        """Test calc with future change"""
        # present
        hazard = Hazard('TC')
        hazard.read_mat(HAZ_TEST_MAT)
        entity = Entity()
        entity.read_excel(ENT_DEMO_TODAY)
        entity.exposures.rename(columns={'if_': 'if_TC'}, inplace=True)
        entity.check()
        entity.exposures.ref_year = 2018

        # future
        ent_future = Entity()
        ent_future.read_excel(ENT_DEMO_FUTURE)
        ent_future.check()
        ent_future.exposures.ref_year = 2040

        haz_future = copy.deepcopy(hazard)
        haz_future.intensity.data += 25

        cost_ben = CostBenefit()
        cost_ben.calc(hazard, entity, haz_future, ent_future)

        self.assertEqual(cost_ben.present_year, 2018)
        self.assertEqual(cost_ben.future_year, 2040)
        self.assertEqual(cost_ben.tot_climate_risk, 5.768659152882021e+11)

        self.assertEqual(cost_ben.imp_meas_present['no measure']['risk'], 6.51220115756442e+09)
        self.assertEqual(cost_ben.imp_meas_present['Mangroves']['risk'], 4.850407096284983e+09)
        self.assertEqual(cost_ben.imp_meas_present['Beach nourishment']['risk'], 5.188921355413834e+09)
        self.assertEqual(cost_ben.imp_meas_present['Seawall']['risk'], 4.736400526119911e+09)
        self.assertEqual(cost_ben.imp_meas_present['Building code']['risk'], 4.884150868173321e+09)

        self.assertEqual(cost_ben.imp_meas_future['no measure']['risk'], 5.9506659786664024e+10)
        self.assertEqual(cost_ben.imp_meas_future['Mangroves']['risk'], 4.826231151473135e+10)
        self.assertEqual(cost_ben.imp_meas_future['Beach nourishment']['risk'], 5.0647250923231674e+10)
        self.assertEqual(cost_ben.imp_meas_future['Seawall']['risk'], 21089567135.7345)
        self.assertEqual(cost_ben.imp_meas_future['Building code']['risk'], 4.462999483999791e+10)

    def test_calc_no_change_pass(self):
        """Test calc without future change"""
        hazard = Hazard('TC')
        hazard.read_mat(HAZ_TEST_MAT)
        entity = Entity()
        entity.read_excel(ENT_DEMO_TODAY)
        entity.check()
        entity.exposures.ref_year = 2018
        cost_ben = CostBenefit()
        cost_ben.calc(hazard, entity, future_year=2040)

        self.assertEqual(cost_ben.imp_meas_present, dict())
        self.assertEqual(len(cost_ben.imp_meas_future), 5)
        self.assertEqual(cost_ben.present_year, 2018)
        self.assertEqual(cost_ben.future_year, 2040)

        self.assertEqual(cost_ben.cost_ben_ratio['Mangroves'], 0.04230714690616641)
        self.assertEqual(cost_ben.cost_ben_ratio['Beach nourishment'], 0.06998836431681373)
        self.assertEqual(cost_ben.cost_ben_ratio['Seawall'], 0.2679741183248266)
        self.assertEqual(cost_ben.cost_ben_ratio['Building code'], 0.30286828677985717)

        self.assertEqual(cost_ben.benefit['Mangroves'], 3.100583368954022e+10)
        self.assertEqual(cost_ben.benefit['Beach nourishment'], 2.468981832719974e+10)
        self.assertEqual(cost_ben.benefit['Seawall'], 3.3132973770502796e+10)
        self.assertEqual(cost_ben.benefit['Building code'], 3.0376240767284798e+10)

        self.assertEqual(cost_ben.tot_climate_risk, 1.2150496306913972e+11)

class TestRiskFuncs(unittest.TestCase):
    '''Test risk functions definitions'''

    def test_impact(self):
        ent = Entity()
        ent.read_excel(ENT_DEMO_TODAY)
        ent.check()
        hazard = Hazard('TC')
        hazard.read_mat(HAZ_TEST_MAT)
        impact = Impact()
        ent.exposures.assign_centroids(hazard)
        impact.calc(ent.exposures, ent.impact_funcs, hazard)
        return impact

    def test_risk_aai_agg_pass(self):
        """Test risk_aai_agg"""
        impact = self.test_impact()
        risk = risk_aai_agg(impact)
        self.assertAlmostEqual(6.512201157564421e+09, risk, 5)
        self.assertTrue(np.isclose(6.512201157564421e+09, risk))

    def test_risk_rp_100_pass(self):
        """Test risk_rp_100"""
        impact = self.test_impact()
        exc_freq = impact.calc_freq_curve([100])

        risk = risk_rp_100(impact)
        self.assertAlmostEqual(exc_freq.impact[0], risk)

    def test_risk_rp_200_pass(self):
        """Test risk_rp_200"""
        impact = self.test_impact()
        exc_freq = impact.calc_freq_curve([250])

        risk = risk_rp_250(impact)
        self.assertAlmostEqual(exc_freq.impact[0], risk)

# Execute Tests
TESTS = unittest.TestLoader().loadTestsFromTestCase(TestRiskFuncs)
TESTS = unittest.TestLoader().loadTestsFromTestCase(TestCalc)
TESTS.addTests(unittest.TestLoader().loadTestsFromTestCase(TestSteps))
TESTS.addTests(unittest.TestLoader().loadTestsFromTestCase(TestRiskFuncs))
unittest.TextTestRunner(verbosity=2).run(TESTS)
