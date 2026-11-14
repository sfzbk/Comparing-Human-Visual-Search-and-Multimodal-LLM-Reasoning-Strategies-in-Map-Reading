result_xlsx = 'test_result/test_result_glm.xlsx'  # Result file

cfg_read = {
    'name': 'ai读图',
    'repeat_runs': 30,
    # 'repeat_runs': 1,
    'image_folder1': 'D:/Desktop/test2',   # Original image
    'image_folder2': 'D:/Desktop/test',    # Grid image
    'result_xlsx': result_xlsx,
    'processed_log': 'test_result/log.txt',
    'prompt': "尽可能写出详细的思考过程。",
    # 'model': 'gpt-5',
    # 'model': 'gemini-3-pro',
    # 'model': 'grok-4.1-fast',
    # 'model': 'grok-4',
    # 'model': 'grok-4-fast',
    # 'model': 'qwen3-vl-8b-thinking',
    'model': 'glm-4.6v',
    # 'model': 'ernie-4.5-vl-424b-a47b',
    # 'model': 'hunyuan-t1-vision-20250916',
    # 'model': 'claude-sonnet-4.5', # Network connection consistently fails
    # 'model': 'claude-opus-4.5',
    # 'model': 'claude-haiku-4.5',
    # 'model': 'gemini-2.5-flash',
    'user_prompt': """
     识别这两张图片，分别是原图和网格版本。
     你需要根据原图顶部的指示分析，鼠标需要点击什么。请用纯文本格式写出详细的分析过程。
     你需要在分析里将每个涉及到网格位置的信息用[网格名]进行标注。
     例如：题目要求“位于xx县”[B2]，图例第三档（201–300）[G1]对应中等偏大的圆。
      """,
    # 'answer_strip': '答案是'
}

cfg_code = {
    'name': '编码整理',
    'result_xlsx': result_xlsx,  # Result file (contains the answers from the previous image-reading step)
    'contents': '''
    提取文字中所有用[]标注的网格信息（如：[A4], [D4]-[F4]等），
    并且输出为['xx', 'xx', ...]的格式（如：['A4', 'D4']）。其中，字母和数字分别代表行号和列号。
    注意：
    1. 如果出现了类似于 [D4]-[F4]的形式，需要把它包含的所有网格都列出来，即D4,E4,F4。
    2. 如果[]内包含其他文字，应该把文字剔除。
    3. 如果出现了类似于[D4]/[E4]的形式，需要转换成符合要求的格式，如['D4', 'E4']。
    4. 必须严格按照原文的顺序，提取所有网格信息。
    5. 只需要输出为['xx', 'xx', ...]的格式，无需解释。
    ''',
    # 'model': 'gemini-2.5-flash',
    'model': 'gpt-5',
}

################### Improved prompt version ###################


tips_from_human = '''
        1. 分析题目后不要急于分析图例，而是先观察地图中具体情况和题目之间的联系。
        2. 观察分析整张地图时，应该多回到题目中，检查地图和题目的联系。
        3. 结合地图分析题目时，不要急于检查图例或者只分析地图本身，而是多回过头思考题目本身的含义。
        4. 结合题目分析图例时，要多思考题目本身的含义、图例和地图的关系，而不要急于根据题目之间寻找答案。
        5. 使用图例信息后，应该多结合问题分析总体情况。
        6. 分析和答案相关的关键图例时，不要急于回到地图中寻找答案，而是回到题目中，确认图例和题目的关系；再次检查图例中的其他部分，确认无误。
        7. 对比候选目标时，不要急于确认正确答案，而是再次检查题目的含义。'''
tips_from_ai = '''
        1. 阅读题目后不要急于确认图例和答案，而是先多观察整张地图
        2. 使用图例信息时，不要急于回到地图中寻找答案，而是先确保图例都仔细看完了
        3. 得到几个有可能的目标后，不要急于进行下一步分析，而是再观察确认一下整个地图
        4. 确认最终答案时，不要局限在几个有可能的目标里面反复对比，而是再看一下地图的其他部分、确认一下题目要求'''
tips_from_all = '''
        1. 分析题目之后不要急于分析图例，而是先观察地图中具体情况和题目之间的联系。
        2. 结合地图分析题目时，不要急于检查图例或者只分析地图本身，而是多回过头来再次思考题目本身。
        3. 阅读地图时，应该反复检查题目要求、并对比确认它们之间的联系。
        4. 结合题目分析图例时，要多思考题目本身的含义、图例和地图的关系，而不要急于根据题目直接寻找答案。
        5. 阅读图例时，不要急于直接回到地图中寻找目标，而是确认把图例读完、检查题目要求。
        6. 确认答案的时候不要一直在地图里搜索，而是要多检查、分析题目要求。'''

result_xlsx2 = 'test_result/test_result2_qwen.xlsx'  # Result file

cfg_read2 = {
    'name': 'ai读图',
    'repeat_runs': 30,
    # 'repeat_runs': 5,
    'image_folder1': 'D:/Desktop/test22',   # Original image
    'image_folder2': 'D:/Desktop/test',    # Grid image
    'result_xlsx': result_xlsx2,
    'processed_log': 'test_result/log.txt',
    'prompt': "尽可能写出详细的思考过程。",
    # 'model': 'gpt-5',
    # 'model': 'gemini-3-pro',    # Model officially discontinued by Google
    # 'model': 'grok-4.1-fast',
    # 'model': 'grok-4',
    # 'model': 'grok-4-fast',
    'model': 'qwen3-vl-8b-thinking',
    # 'model': 'glm-4.6v',
    # 'model': 'ernie-4.5-vl-424b-a47b',
    # 'model': 'hunyuan-t1-vision-20250916',
    # 'model': 'claude-sonnet-4.5', # Network connection consistently fails
    # 'model': 'claude-opus-4.5',
    # 'model': 'claude-haiku-4.5',
    # 'model': 'gemini-2.5-flash',
    'user_prompt': f"""
     识别这两张图片，分别是原图和网格版本。
     你需要根据原图顶部的指示分析，鼠标需要点击什么。请用纯文本格式写出详细的分析过程。
     你需要在分析里将每个涉及到网格位置的信息用[网格名]进行标注。
     例如：题目要求“位于xx县”[B2]，图例第三档（201–300）[G1]对应中等偏大的圆。
     注意事项：
     {tips_from_all}
      """,
    # 'answer_strip': '答案是'
}
