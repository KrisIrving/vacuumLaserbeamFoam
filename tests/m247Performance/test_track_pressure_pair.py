import copy
from pathlib import Path
import unittest
from unittest.mock import patch
from track_pressure_pair import geometry_difference, pressure_stats, validate_source
from track1500_pilot import TEMPLATE

class PressurePairTest(unittest.TestCase):
    def test_pressure_final_requires_absolute_tolerance(self):
        def log(final):
            return '\n'.join(f'GAMG: Solving for p_rgh, Initial residual = 0.001, Final residual = {r}, No Iterations 4\ntime step continuity errors : sum local = 1e-9, global = 1e-12, cumulative = 1e-10' for r in (1e-5,1e-5,final))
        self.assertTrue(pressure_stats(log(9e-8),1)['passed'])
        self.assertTrue(pressure_stats('time step continuity errors : sum local = 0, global = 0, cumulative = 0\n'+log(9e-8),1)['passed'])
        with self.assertRaises(ValueError):pressure_stats('time step continuity errors : sum local = 1, global = 0, cumulative = 0\n'+log(9e-8),1)
        self.assertFalse(pressure_stats(log(1e-6),1)['passed'])
        with self.assertRaises(ValueError):pressure_stats(log(9e-8),2)
        with self.assertRaises(ValueError):pressure_stats(log(9e-8)+' nan',1)

    def test_geometry_checks_both_dimensions_without_temperature_gate(self):
        a=dict(solidus_connected_pool=dict(depth_from_original_surface_um=100,width_z_um=200),temperature_maxima_K={'gas':4000})
        b=copy.deepcopy(a);b['temperature_maxima_K']['gas']=8000;b['solidus_connected_pool']['depth_from_original_surface_um']=104
        self.assertTrue(geometry_difference(a,b)['passed'])
        b['solidus_connected_pool']['width_z_um']=211
        self.assertFalse(geometry_difference(a,b)['passed'])
        self.assertFalse(geometry_difference({'solidus_connected_pool':None},b)['passed'])

    def test_source_queries_match_committed_dictionary_names(self):
        # A fake official dictionary query backed by the real template catches
        # misspelled entries before asking Ubuntu to run them.
        import re
        summary={'steps':1,'thermal_limit_hits':0};meta={'ranks':48,'end_s':50e-6}
        def exists(p):return p.name!='dynamicMeshDict'
        with patch('track_pressure_pair.read_probe',return_value=(meta,summary,[])),patch('track_pressure_pair.residual_gate',return_value=True),patch('pathlib.Path.read_text',return_value='End\n') as read,patch('pathlib.Path.glob',return_value=[Path('source/processor'+str(i)) for i in range(48)]),patch('pathlib.Path.is_dir',return_value=True),patch('pathlib.Path.exists',exists),patch('track_pressure_pair.checkpoint',side_effect=lambda rank,t:rank/'5e-05'):
            # Actual template reads must bypass the completed-source-log mock.
            original=Path.open
            def real_query(command,**kw):
                dictionary=Path(command[1]).relative_to(Path('source'))
                with original(TEMPLATE/dictionary) as handle:text=handle.read()
                name=command[command.index('-entry')+1].split('/')[-1]
                if not re.search(r'\b'+re.escape(name)+r'\s+',text):raise ValueError('Missing key '+name)
                if name=='solver':return 'PCG'
                if name=='tolerance':return '1e-7'
                if name=='relTol':return '0' if 'p_rghFinal' in command[command.index('-entry')+1] else '.05'
                return re.findall(r'\b'+re.escape(name)+r'\s+([^;{}]+);',text)[-1]
            with patch('subprocess.check_output',side_effect=real_query):validate_source(Path('source'))

if __name__=='__main__':unittest.main()
