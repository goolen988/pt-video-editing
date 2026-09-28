import importlib.util,json,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
ed=module('edit',ROOT/'skills/pt-video-editing/scripts/edit.py');installer=module('installer',ROOT/'install.py')
class Core(unittest.TestCase):
 def test_reorder_remaps_words(self):
  w=[{'w':'first','s':.2,'e':.6},{'w':'second','s':2.2,'e':2.6}]
  mapped,spans,total=ed.timeline([{'start':2,'end':3},{'start':0,'end':1}],w,3)
  self.assertEqual([x['w'] for x in mapped],['second','first']);self.assertEqual(mapped[1]['s'],1.2);self.assertEqual(total,2);self.assertEqual(spans[0]['source_start'],2)
 def test_frame_grid_accumulation(self):
  w=[{'w':'next','s':.2,'e':.3}]
  mapped,spans,total=ed.timeline([{'start':0,'end':.101}]*100,w,1,30)
  self.assertAlmostEqual(total,100*4/30)
  self.assertEqual(spans[-1]['frames'],4)
  self.assertLess(spans[-1]['tail_hold'],1/30)
 def test_no_partial_word(self):
  with self.assertRaises(ValueError):ed.timeline([{'start':.3,'end':1}],[{'w':'not','s':.2,'e':.6}],2)
 def test_invalid_ranges(self):
  for a,b in [(1,0),(-1,1),(0,5),(0,float('nan'))]:
   with self.assertRaises(ValueError):ed.timeline([{'start':a,'end':b}],[],2)
 def test_face_collision(self):
  p={'cards':[{'start':0,'end':1,'x':.15,'y':.2,'w':.7,'h':.15,'text':'Hello'}],'face_boxes':[{'start':0,'end':1,'x':.3,'y':.25,'w':.2,'h':.2}]}
  with self.assertRaises(ValueError):ed.layout(p,[],2)
 def test_overlap_and_bounds(self):
  p={'cards':[{'start':0,'end':1,'x':.15,'y':.65,'w':.7,'h':.1,'text':'Hello'}]}
  with self.assertRaises(ValueError):ed.layout(p,[{'start':0,'end':1,'text':'Speech'}],2)
  with self.assertRaises(ValueError):ed.layout({'caption_y':.95},[{'start':0,'end':1,'text':'Speech'}],2)
 def test_install_upgrade_preserves_data(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);(root/'source.mp4').write_bytes(b'user footage');first=installer.install(d,'codex','pt-video-editing');target=Path(first['installed']);(target/'local-note').write_text('prior');second=installer.install(d,'codex','pt-video-editing')
   self.assertEqual((root/'source.mp4').read_bytes(),b'user footage');self.assertEqual((Path(second['backup'])/'local-note').read_text(),'prior');self.assertTrue((target/'SKILL.md').exists())
 def test_install_refuses_symlink(self):
  with tempfile.TemporaryDirectory() as d,tempfile.TemporaryDirectory() as outside:
   root=Path(d);(root/'.agents').symlink_to(outside,target_is_directory=True)
   with self.assertRaises(ValueError):installer.install(d,'codex','pt-connect')
if __name__=='__main__':unittest.main()
