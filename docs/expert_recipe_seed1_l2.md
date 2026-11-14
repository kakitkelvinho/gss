# Expert lab recipe (seed 1, level 2)

By-product of the reference run: what the scripted expert did, in order, with lab time.

- OPA wavelength 1300 nm. Parts bought: DL-C25 delay stage, 4 x MIR-1 mirror, 1 x PER-1 periscope, CAM-VSWIR, GAP-TPA (EUR 10350; C_min = EUR 7300)
- Lab time: 152.0 min of 240 (63.3%), 115 tool calls
- Result: eta = 0.9969, R = 0.9070, O = 0.9972, |dt| = 3.2 fs

| # | t (min) | tool | args |
|---|---|---|---|
| 0 | 5.0 | read_manual | `{"device": "table"}` |
| 1 | 10.0 | read_manual | `{"device": "opa"}` |
| 2 | 15.0 | read_manual | `{"device": "delay_stage"}` |
| 3 | 20.0 | read_manual | `{"device": "sample_mount"}` |
| 4 | 35.0 | buy | `{"items": {"DL-C25": 1, "MIR-1": 4, "PER-1": 1, "GAP-TPA": 1, "CAM-VSWIR": 1}}` |
| 5 | 40.1 | place | `{"part": "sample", "x": 1200.0, "z": 600.0, "height": 120.0, "yaw_deg": 0.0}` |
| 6 | 40.2 | unblock | `{"arm": "opa"}` |
| 7 | 45.4 | place | `{"part": "periscope-1", "x": 2050.0, "z": 935.0, "height": 120.0, "yaw_deg": 180.0, "height_in": 158.0}` |
| 8 | 45.9 | ir_card | `{"x": 1461.6295090390227, "z": 935.0, "height": 120.0}` |
| 9 | 46.4 | ir_card | `{"x": 1461.6295090390227, "z": 935.0, "height": 120.0}` |
| 10 | 46.9 | knob | `{"part": "periscope-1", "axis": "yaw", "delta_mrad": 5.0988}` |
| 11 | 47.4 | ir_card | `{"x": 1461.6295090390227, "z": 935.0, "height": 120.0}` |
| 12 | 47.9 | knob | `{"part": "periscope-1", "axis": "pitch", "delta_mrad": 5.0988}` |
| 13 | 48.4 | ir_card | `{"x": 1461.6295090390227, "z": 935.0, "height": 120.0}` |
| 14 | 49.0 | knob | `{"part": "periscope-1", "axis": "yaw", "delta_mrad": -7.0432}` |
| 15 | 49.5 | knob | `{"part": "periscope-1", "axis": "pitch", "delta_mrad": -5.5161}` |
| 16 | 50.0 | ir_card | `{"x": 1461.6295090390227, "z": 935.0, "height": 120.0}` |
| 17 | 50.5 | knob | `{"part": "periscope-1", "axis": "yaw", "delta_mrad": -0.7803}` |
| 18 | 51.0 | knob | `{"part": "periscope-1", "axis": "pitch", "delta_mrad": -0.6926}` |
| 19 | 51.5 | ir_card | `{"x": 1461.6295090390227, "z": 935.0, "height": 120.0}` |
| 20 | 56.5 | place | `{"part": "mirror-1", "x": 1461.6295090390227, "z": 935.0, "height": 120.0, "yaw_deg": -45.0}` |
| 21 | 57.0 | ir_card | `{"x": 1461.6295090390227, "z": 861.6295090390227, "height": 120.0}` |
| 22 | 57.5 | ir_card | `{"x": 1461.6295090390227, "z": 861.6295090390227, "height": 120.0}` |
| 23 | 58.0 | knob | `{"part": "mirror-1", "axis": "yaw", "delta_mrad": 40.8884}` |
| 24 | 58.5 | ir_card | `{"x": 1461.6295090390227, "z": 861.6295090390227, "height": 120.0}` |
| 25 | 59.0 | knob | `{"part": "mirror-1", "axis": "pitch", "delta_mrad": 40.8884}` |
| 26 | 59.5 | ir_card | `{"x": 1461.6295090390227, "z": 861.6295090390227, "height": 120.0}` |
| 27 | 60.0 | knob | `{"part": "mirror-1", "axis": "yaw", "delta_mrad": -16.4774}` |
| 28 | 60.5 | knob | `{"part": "mirror-1", "axis": "pitch", "delta_mrad": -20.0}` |
| 29 | 61.0 | ir_card | `{"x": 1461.6295090390227, "z": 861.6295090390227, "height": 120.0}` |
| 30 | 61.5 | knob | `{"part": "mirror-1", "axis": "pitch", "delta_mrad": -20.0}` |
| 31 | 62.0 | ir_card | `{"x": 1461.6295090390227, "z": 861.6295090390227, "height": 120.0}` |
| 32 | 67.0 | place | `{"part": "mirror-2", "x": 1461.6295090390227, "z": 861.6295090390227, "height": 120.0, "yaw_deg": 157.5}` |
| 33 | 67.5 | ir_card | `{"x": 1270.7106781186546, "z": 670.7106781186548, "height": 120.0}` |
| 34 | 68.0 | ir_card | `{"x": 1270.7106781186546, "z": 670.7106781186548, "height": 120.0}` |
| 35 | 68.5 | knob | `{"part": "mirror-2", "axis": "yaw", "delta_mrad": 11.1111}` |
| 36 | 69.0 | ir_card | `{"x": 1270.7106781186546, "z": 670.7106781186548, "height": 120.0}` |
| 37 | 69.6 | knob | `{"part": "mirror-2", "axis": "pitch", "delta_mrad": 11.1111}` |
| 38 | 70.1 | ir_card | `{"x": 1270.7106781186546, "z": 670.7106781186548, "height": 120.0}` |
| 39 | 70.6 | knob | `{"part": "mirror-2", "axis": "yaw", "delta_mrad": 10.5976}` |
| 40 | 71.1 | knob | `{"part": "mirror-2", "axis": "pitch", "delta_mrad": -15.0815}` |
| 41 | 71.6 | ir_card | `{"x": 1270.7106781186546, "z": 670.7106781186548, "height": 120.0}` |
| 42 | 72.1 | knob | `{"part": "mirror-2", "axis": "yaw", "delta_mrad": -0.4836}` |
| 43 | 72.6 | knob | `{"part": "mirror-2", "axis": "pitch", "delta_mrad": 2.5912}` |
| 44 | 73.1 | ir_card | `{"x": 1270.7106781186546, "z": 670.7106781186548, "height": 120.0}` |
| 45 | 73.3 | unblock | `{"arm": "800nm"}` |
| 46 | 78.3 | place | `{"part": "stage", "x": 873.6118318204308, "z": 309.0, "height": 120.0, "yaw_deg": 180.0}` |
| 47 | 78.8 | ir_card | `{"x": 1546.4823227814081, "z": 324.0, "height": 120.0}` |
| 48 | 83.8 | place | `{"part": "mirror-3", "x": 1546.4823227814081, "z": 325.9, "height": 119.3, "yaw_deg": 225.0}` |
| 49 | 84.3 | ir_card | `{"x": 1546.4823227814081, "z": 253.51767721859176, "height": 120.0}` |
| 50 | 84.8 | ir_card | `{"x": 1546.4823227814081, "z": 253.51767721859176, "height": 120.0}` |
| 51 | 85.3 | knob | `{"part": "mirror-3", "axis": "yaw", "delta_mrad": 41.4466}` |
| 52 | 85.8 | ir_card | `{"x": 1546.4823227814081, "z": 253.51767721859176, "height": 120.0}` |
| 53 | 86.3 | knob | `{"part": "mirror-3", "axis": "pitch", "delta_mrad": 41.4466}` |
| 54 | 86.8 | ir_card | `{"x": 1546.4823227814081, "z": 253.51767721859176, "height": 120.0}` |
| 55 | 87.3 | knob | `{"part": "mirror-3", "axis": "yaw", "delta_mrad": -20.0}` |
| 56 | 87.8 | knob | `{"part": "mirror-3", "axis": "pitch", "delta_mrad": -20.0}` |
| 57 | 88.3 | ir_card | `{"x": 1546.4823227814081, "z": 253.51767721859176, "height": 120.0}` |
| 58 | 88.8 | knob | `{"part": "mirror-3", "axis": "yaw", "delta_mrad": -18.8026}` |
| 59 | 89.3 | knob | `{"part": "mirror-3", "axis": "pitch", "delta_mrad": -15.7699}` |
| 60 | 89.8 | ir_card | `{"x": 1546.4823227814081, "z": 253.51767721859176, "height": 120.0}` |
| 61 | 90.3 | knob | `{"part": "mirror-3", "axis": "yaw", "delta_mrad": 3.1506}` |
| 62 | 90.8 | knob | `{"part": "mirror-3", "axis": "pitch", "delta_mrad": -4.5996}` |
| 63 | 91.3 | ir_card | `{"x": 1546.4823227814081, "z": 253.51767721859176, "height": 120.0}` |
| 64 | 96.3 | place | `{"part": "mirror-4", "x": 1546.4823227814081, "z": 253.51767721859176, "height": 120.0, "yaw_deg": 112.5}` |
| 65 | 96.9 | ir_card | `{"x": 1270.7106781186546, "z": 529.2893218813452, "height": 120.0}` |
| 66 | 97.4 | ir_card | `{"x": 1270.7106781186546, "z": 529.2893218813452, "height": 120.0}` |
| 67 | 97.9 | knob | `{"part": "mirror-4", "axis": "yaw", "delta_mrad": 7.6923}` |
| 68 | 98.4 | ir_card | `{"x": 1270.7106781186546, "z": 529.2893218813452, "height": 120.0}` |
| 69 | 98.9 | knob | `{"part": "mirror-4", "axis": "pitch", "delta_mrad": 7.6923}` |
| 70 | 99.4 | ir_card | `{"x": 1270.7106781186546, "z": 529.2893218813452, "height": 120.0}` |
| 71 | 99.9 | knob | `{"part": "mirror-4", "axis": "yaw", "delta_mrad": 10.9505}` |
| 72 | 100.4 | knob | `{"part": "mirror-4", "axis": "pitch", "delta_mrad": -7.3816}` |
| 73 | 100.9 | ir_card | `{"x": 1270.7106781186546, "z": 529.2893218813452, "height": 120.0}` |
| 74 | 101.4 | knob | `{"part": "mirror-4", "axis": "yaw", "delta_mrad": 0.7611}` |
| 75 | 101.9 | knob | `{"part": "mirror-4", "axis": "pitch", "delta_mrad": -0.2437}` |
| 76 | 102.4 | ir_card | `{"x": 1270.7106781186546, "z": 529.2893218813452, "height": 120.0}` |
| 77 | 102.9 | knob | `{"part": "mirror-4", "axis": "yaw", "delta_mrad": 0.7526}` |
| 78 | 103.4 | knob | `{"part": "mirror-4", "axis": "pitch", "delta_mrad": -0.5003}` |
| 79 | 103.9 | ir_card | `{"x": 1270.7106781186546, "z": 529.2893218813452, "height": 120.0}` |
| 80 | 104.5 | knob | `{"part": "mirror-4", "axis": "yaw", "delta_mrad": -1.0219}` |
| 81 | 105.0 | knob | `{"part": "mirror-4", "axis": "pitch", "delta_mrad": 0.1112}` |
| 82 | 105.5 | ir_card | `{"x": 1270.7106781186546, "z": 529.2893218813452, "height": 120.0}` |
| 83 | 105.6 | block | `{"arm": "800nm"}` |
| 84 | 105.8 | view_camera | `{"plane": "sample"}` |
| 85 | 105.9 | unblock | `{"arm": "800nm"}` |
| 86 | 106.0 | view_camera | `{"plane": "sample"}` |
| 87 | 106.2 | view_camera | `{"plane": "sample"}` |
| 88 | 106.8 | knob | `{"part": "mirror-4", "axis": "yaw", "delta_mrad": 0.3}` |
| 89 | 107.1 | view_camera | `{"plane": "sample"}` |
| 90 | 107.2 | view_camera | `{"plane": "sample"}` |
| 91 | 107.8 | knob | `{"part": "mirror-4", "axis": "pitch", "delta_mrad": 0.3}` |
| 92 | 108.1 | view_camera | `{"plane": "sample"}` |
| 93 | 108.2 | view_camera | `{"plane": "sample"}` |
| 94 | 108.8 | knob | `{"part": "mirror-4", "axis": "yaw", "delta_mrad": -0.5351}` |
| 95 | 109.3 | knob | `{"part": "mirror-4", "axis": "pitch", "delta_mrad": 0.0537}` |
| 96 | 109.6 | view_camera | `{"plane": "sample"}` |
| 97 | 109.8 | view_camera | `{"plane": "sample"}` |
| 98 | 110.4 | knob | `{"part": "mirror-4", "axis": "yaw", "delta_mrad": 0.0683}` |
| 99 | 110.9 | knob | `{"part": "mirror-4", "axis": "pitch", "delta_mrad": -0.0429}` |
| 100 | 111.1 | view_camera | `{"plane": "sample"}` |
| 101 | 111.3 | view_camera | `{"plane": "sample"}` |
| 102 | 111.9 | knob | `{"part": "mirror-4", "axis": "yaw", "delta_mrad": -0.0099}` |
| 103 | 112.4 | knob | `{"part": "mirror-4", "axis": "pitch", "delta_mrad": 0.0106}` |
| 104 | 112.6 | view_camera | `{"plane": "sample"}` |
| 105 | 112.8 | view_camera | `{"plane": "sample"}` |
| 106 | 115.8 | measure_path | `{"arm": "800nm"}` |
| 107 | 118.8 | measure_path | `{"arm": "opa"}` |
| 108 | 118.9 | status | `{}` |
| 109 | 147.1 | scan | `{"start_mm": 8.6, "end_mm": 20.6, "step_mm": 0.005, "t_int": 0.4}` |
| 110 | 151.5 | scan | `{"start_mm": 15.3185, "end_mm": 15.5415, "step_mm": 0.002, "t_int": 2.0}` |
| 111 | 151.5 | move_stage | `{"position_mm": 15.43749}` |
| 112 | 151.7 | view_camera | `{"plane": "sample"}` |
| 113 | 151.9 | view_camera | `{"plane": "sample"}` |
| 114 | 152.0 | submit | `{}` |
