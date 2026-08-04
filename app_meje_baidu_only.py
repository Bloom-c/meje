# ============================================================
# TAB 1: 发现引擎（修复版）
# ============================================================
with tab_main:
    st.markdown("##### 选择使用场景")
    
    if 'mode_selected' not in st.session_state:
        st.session_state.mode_selected = "销售"
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💼 销售模式\n找潜在客户", use_container_width=True, key="mode_sales"):
            st.session_state.mode_selected = "销售"
            st.rerun()
    with col2:
        if st.button("🎓 求职模式\n找理想雇主", use_container_width=True, key="mode_job"):
            st.session_state.mode_selected = "求职"
            st.rerun()
    
    mode_key = st.session_state.mode_selected
    st.markdown(f'<div style="background:linear-gradient(135deg,#667eea,#764ba2);color:white;padding:10px 20px;border-radius:10px;text-align:center;font-weight:600;margin:8px 0 12px 0;">✅ 当前模式：{"💼 销售" if mode_key == "销售" else "🎓 求职"}</div>', unsafe_allow_html=True)
    
    # ===== AI 帮你写需求 =====
    with st.expander("🤖 AI 帮我写需求描述", expanded=False):
        st.caption("💡 填写信息后点击生成，AI 会自动生成需求描述，然后点击「填入输入框」")
        
        if mode_key == "销售":
            col_a, col_b = st.columns(2)
            with col_a:
                product = st.text_input("产品/服务", placeholder="AI客服系统", key="p1")
                target_industry = st.text_input("目标行业", placeholder="电商", key="p2")
            with col_b:
                target_size = st.text_input("目标规模", placeholder="500人以上", key="p3")
                pain_point = st.text_input("客户痛点", placeholder="客服响应慢", key="p4")
            extra = st.text_area("补充信息", placeholder="最近有融资的优先", key="p5", height=40)
        else:
            col_a, col_b = st.columns(2)
            with col_a:
                skill = st.text_input("核心技能", placeholder="前端开发", key="j1")
                tech_stack = st.text_input("技术栈", placeholder="React, TypeScript", key="j2")
            with col_b:
                target_industry_job = st.text_input("目标行业", placeholder="互联网", key="j3")
                job_level = st.text_input("目标职级", placeholder="中级", key="j4")
            extra = st.text_area("补充信息", placeholder="希望公司已盈利", key="j5", height=40)
        
        if st.button("🚀 生成需求描述", use_container_width=True, key="gen_btn"):
            if mode_key == "销售":
                info = f"产品：{product or '未填写'}\n行业：{target_industry or '未填写'}\n规模：{target_size or '未填写'}\n痛点：{pain_point or '未填写'}\n补充：{extra or '无'}"
                prompt_text = f"你是商业需求分析师。生成一段专业完整的需求描述（150-200字）。用户信息：\n{info}\n要求：直接输出描述，不要有其他内容。"
            else:
                info = f"技能：{skill or '未填写'}\n技术栈：{tech_stack or '未填写'}\n目标行业：{target_industry_job or '未填写'}\n职级：{job_level or '未填写'}\n补充：{extra or '无'}"
                prompt_text = f"你是职业规划师。生成一段专业完整的求职需求描述（150-200字）。用户信息：\n{info}\n要求：直接输出描述，不要有其他内容。"
            
            with st.spinner("🤖 AI 生成中..."):
                try:
                    resp = client.chat.completions.create(
                        model="deepseek-chat",
                        messages=[{"role": "system", "content": "你是专业文案助手。"}, {"role": "user", "content": prompt_text}],
                        temperature=0.7,
                        max_tokens=800
                    )
                    generated_text = resp.choices[0].message.content
                    st.session_state.generated_need = generated_text
                    
                    st.markdown("##### ✅ 生成结果：")
                    st.info(generated_text)
                    
                    if st.button("📥 填入输入框", use_container_width=True, key="fill_btn"):
                        # 直接修改 session_state 中 text_area 对应的 key
                        st.session_state.need_input = generated_text
                        st.success("✅ 已填入输入框！")
                        
                except Exception as e:
                    st.error(f"生成失败: {str(e)}")
    
    # ===== 需求输入框 =====
    # 初始化
    if 'need_input' not in st.session_state:
        st.session_state.need_input = ""
    
    # 用 key 直接绑定，不写 value
    st.text_area(
        "📝 描述你的需求",
        height=120,
        placeholder="示例：我销售AI客服系统，目标客户是电商和零售公司，有客服团队，最近有融资或扩张计划。",
        key="need_input"
    )
    
    if st.button("🔍 开始搜索", use_container_width=True, type="primary"):
        # 从 session_state 读取
        need_description = st.session_state.get("need_input", "")
        if not need_description:
            st.error("⚠️ 请先输入需求描述")
        else:
            result_df = quick_search(need_description, mode_key)
            if not result_df.empty:
                result_df = result_df.sort_values("综合评分", ascending=False)
                
                st.markdown("---")
                st.markdown(f"##### 📊 搜索结果 · 共 {len(result_df)} 家公司")
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("🏢 公司总数", len(result_df))
                with col2:
                    st.metric("🔥 高优先级", len(result_df[result_df['优先级'].str.contains('高')]))
                with col3:
                    st.metric("📊 平均评分", int(result_df['综合评分'].mean()))
                with col4:
                    st.metric("📡 数据源", len(result_df['数据来源'].unique()))
                
                st.markdown("---")
                
                for _, row in result_df.iterrows():
                    score = row['综合评分']
                    priority = row['优先级']
                    p_class = "priority-high" if "高" in str(priority) else "priority-mid" if "中" in str(priority) else "priority-low"
                    p_label = "🔥 高优先级" if "高" in str(priority) else "📌 中优先级" if "中" in str(priority) else "💤 低优先级"
                    
                    st.markdown(f"""
                    <div class="company-card">
                        <div style="display:flex;justify-content:space-between;align-items:center;">
                            <div><strong>{row['公司名称']}</strong> <span class="{p_class}">{p_label}</span></div>
                            <div><span style="font-size:24px;font-weight:700;color:#667eea;">{score}</span></div>
                        </div>
                        <div style="margin-top:6px;display:flex;flex-wrap:wrap;gap:4px;">
                            <span class="tag">🎯 匹配度: {row.get('匹配度', 'N/A')}</span>
                            <span class="tag">📡 {row.get('数据来源', '')}</span>
                            {f'<span class="tag">👤 {row["创始人"]}</span>' if row.get('创始人') else ''}
                            {f'<span class="tag">📅 {row["成立时间"]}</span>' if row.get('成立时间') else ''}
                            {f'<span class="tag">💼 {row["招聘数"]}个岗位</span>' if row.get('招聘数', 0) > 0 else ''}
                        </div>
                        <div style="margin-top:6px;font-size:14px;color:#3c4043;">{row.get('理由', '')[:100]}</div>
                        <div style="font-size:13px;color:#667eea;">💡 {row.get('建议动作', '')}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                csv = result_df.to_csv(index=False).encode('utf-8-sig')
                st.download_button("📥 下载结果 (CSV)", data=csv, file_name=f"觅镜_结果_{datetime.now().strftime('%Y%m%d')}.csv", mime="text/csv", use_container_width=True)# ============================================================
# TAB 1: 发现引擎（修复版）
# ============================================================
with tab_main:
    st.markdown("##### 选择使用场景")
    
    if 'mode_selected' not in st.session_state:
        st.session_state.mode_selected = "销售"
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💼 销售模式\n找潜在客户", use_container_width=True, key="mode_sales"):
            st.session_state.mode_selected = "销售"
            st.rerun()
    with col2:
        if st.button("🎓 求职模式\n找理想雇主", use_container_width=True, key="mode_job"):
            st.session_state.mode_selected = "求职"
            st.rerun()
    
    mode_key = st.session_state.mode_selected
    st.markdown(f'<div style="background:linear-gradient(135deg,#667eea,#764ba2);color:white;padding:10px 20px;border-radius:10px;text-align:center;font-weight:600;margin:8px 0 12px 0;">✅ 当前模式：{"💼 销售" if mode_key == "销售" else "🎓 求职"}</div>', unsafe_allow_html=True)
    
    # ===== AI 帮你写需求 =====
    with st.expander("🤖 AI 帮我写需求描述", expanded=False):
        st.caption("💡 填写信息后点击生成，AI 会自动生成需求描述，然后点击「填入输入框」")
        
        if mode_key == "销售":
            col_a, col_b = st.columns(2)
            with col_a:
                product = st.text_input("产品/服务", placeholder="AI客服系统", key="p1")
                target_industry = st.text_input("目标行业", placeholder="电商", key="p2")
            with col_b:
                target_size = st.text_input("目标规模", placeholder="500人以上", key="p3")
                pain_point = st.text_input("客户痛点", placeholder="客服响应慢", key="p4")
            extra = st.text_area("补充信息", placeholder="最近有融资的优先", key="p5", height=40)
        else:
            col_a, col_b = st.columns(2)
            with col_a:
                skill = st.text_input("核心技能", placeholder="前端开发", key="j1")
                tech_stack = st.text_input("技术栈", placeholder="React, TypeScript", key="j2")
            with col_b:
                target_industry_job = st.text_input("目标行业", placeholder="互联网", key="j3")
                job_level = st.text_input("目标职级", placeholder="中级", key="j4")
            extra = st.text_area("补充信息", placeholder="希望公司已盈利", key="j5", height=40)
        
        if st.button("🚀 生成需求描述", use_container_width=True, key="gen_btn"):
            if mode_key == "销售":
                info = f"产品：{product or '未填写'}\n行业：{target_industry or '未填写'}\n规模：{target_size or '未填写'}\n痛点：{pain_point or '未填写'}\n补充：{extra or '无'}"
                prompt_text = f"你是商业需求分析师。生成一段专业完整的需求描述（150-200字）。用户信息：\n{info}\n要求：直接输出描述，不要有其他内容。"
            else:
                info = f"技能：{skill or '未填写'}\n技术栈：{tech_stack or '未填写'}\n目标行业：{target_industry_job or '未填写'}\n职级：{job_level or '未填写'}\n补充：{extra or '无'}"
                prompt_text = f"你是职业规划师。生成一段专业完整的求职需求描述（150-200字）。用户信息：\n{info}\n要求：直接输出描述，不要有其他内容。"
            
            with st.spinner("🤖 AI 生成中..."):
                try:
                    resp = client.chat.completions.create(
                        model="deepseek-chat",
                        messages=[{"role": "system", "content": "你是专业文案助手。"}, {"role": "user", "content": prompt_text}],
                        temperature=0.7,
                        max_tokens=800
                    )
                    generated_text = resp.choices[0].message.content
                    st.session_state.generated_need = generated_text
                    
                    st.markdown("##### ✅ 生成结果：")
                    st.info(generated_text)
                    
                    if st.button("📥 填入输入框", use_container_width=True, key="fill_btn"):
                        # 直接修改 session_state 中 text_area 对应的 key
                        st.session_state.need_input = generated_text
                        st.success("✅ 已填入输入框！")
                        
                except Exception as e:
                    st.error(f"生成失败: {str(e)}")
    
    # ===== 需求输入框 =====
    # 初始化
    if 'need_input' not in st.session_state:
        st.session_state.need_input = ""
    
    # 用 key 直接绑定，不写 value
    st.text_area(
        "📝 描述你的需求",
        height=120,
        placeholder="示例：我销售AI客服系统，目标客户是电商和零售公司，有客服团队，最近有融资或扩张计划。",
        key="need_input"
    )
    
    if st.button("🔍 开始搜索", use_container_width=True, type="primary"):
        # 从 session_state 读取
        need_description = st.session_state.get("need_input", "")
        if not need_description:
            st.error("⚠️ 请先输入需求描述")
        else:
            result_df = quick_search(need_description, mode_key)
            if not result_df.empty:
                result_df = result_df.sort_values("综合评分", ascending=False)
                
                st.markdown("---")
                st.markdown(f"##### 📊 搜索结果 · 共 {len(result_df)} 家公司")
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("🏢 公司总数", len(result_df))
                with col2:
                    st.metric("🔥 高优先级", len(result_df[result_df['优先级'].str.contains('高')]))
                with col3:
                    st.metric("📊 平均评分", int(result_df['综合评分'].mean()))
                with col4:
                    st.metric("📡 数据源", len(result_df['数据来源'].unique()))
                
                st.markdown("---")
                
                for _, row in result_df.iterrows():
                    score = row['综合评分']
                    priority = row['优先级']
                    p_class = "priority-high" if "高" in str(priority) else "priority-mid" if "中" in str(priority) else "priority-low"
                    p_label = "🔥 高优先级" if "高" in str(priority) else "📌 中优先级" if "中" in str(priority) else "💤 低优先级"
                    
                    st.markdown(f"""
                    <div class="company-card">
                        <div style="display:flex;justify-content:space-between;align-items:center;">
                            <div><strong>{row['公司名称']}</strong> <span class="{p_class}">{p_label}</span></div>
                            <div><span style="font-size:24px;font-weight:700;color:#667eea;">{score}</span></div>
                        </div>
                        <div style="margin-top:6px;display:flex;flex-wrap:wrap;gap:4px;">
                            <span class="tag">🎯 匹配度: {row.get('匹配度', 'N/A')}</span>
                            <span class="tag">📡 {row.get('数据来源', '')}</span>
                            {f'<span class="tag">👤 {row["创始人"]}</span>' if row.get('创始人') else ''}
                            {f'<span class="tag">📅 {row["成立时间"]}</span>' if row.get('成立时间') else ''}
                            {f'<span class="tag">💼 {row["招聘数"]}个岗位</span>' if row.get('招聘数', 0) > 0 else ''}
                        </div>
                        <div style="margin-top:6px;font-size:14px;color:#3c4043;">{row.get('理由', '')[:100]}</div>
                        <div style="font-size:13px;color:#667eea;">💡 {row.get('建议动作', '')}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                csv = result_df.to_csv(index=False).encode('utf-8-sig')
                st.download_button("📥 下载结果 (CSV)", data=csv, file_name=f"觅镜_结果_{datetime.now().strftime('%Y%m%d')}.csv", mime="text/csv", use_container_width=True)# ============================================================
# TAB 1: 发现引擎（修复版）
# ============================================================
with tab_main:
    st.markdown("##### 选择使用场景")
    
    if 'mode_selected' not in st.session_state:
        st.session_state.mode_selected = "销售"
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💼 销售模式\n找潜在客户", use_container_width=True, key="mode_sales"):
            st.session_state.mode_selected = "销售"
            st.rerun()
    with col2:
        if st.button("🎓 求职模式\n找理想雇主", use_container_width=True, key="mode_job"):
            st.session_state.mode_selected = "求职"
            st.rerun()
    
    mode_key = st.session_state.mode_selected
    st.markdown(f'<div style="background:linear-gradient(135deg,#667eea,#764ba2);color:white;padding:10px 20px;border-radius:10px;text-align:center;font-weight:600;margin:8px 0 12px 0;">✅ 当前模式：{"💼 销售" if mode_key == "销售" else "🎓 求职"}</div>', unsafe_allow_html=True)
    
    # ===== AI 帮你写需求 =====
    with st.expander("🤖 AI 帮我写需求描述", expanded=False):
        st.caption("💡 填写信息后点击生成，AI 会自动生成需求描述，然后点击「填入输入框」")
        
        if mode_key == "销售":
            col_a, col_b = st.columns(2)
            with col_a:
                product = st.text_input("产品/服务", placeholder="AI客服系统", key="p1")
                target_industry = st.text_input("目标行业", placeholder="电商", key="p2")
            with col_b:
                target_size = st.text_input("目标规模", placeholder="500人以上", key="p3")
                pain_point = st.text_input("客户痛点", placeholder="客服响应慢", key="p4")
            extra = st.text_area("补充信息", placeholder="最近有融资的优先", key="p5", height=40)
        else:
            col_a, col_b = st.columns(2)
            with col_a:
                skill = st.text_input("核心技能", placeholder="前端开发", key="j1")
                tech_stack = st.text_input("技术栈", placeholder="React, TypeScript", key="j2")
            with col_b:
                target_industry_job = st.text_input("目标行业", placeholder="互联网", key="j3")
                job_level = st.text_input("目标职级", placeholder="中级", key="j4")
            extra = st.text_area("补充信息", placeholder="希望公司已盈利", key="j5", height=40)
        
        if st.button("🚀 生成需求描述", use_container_width=True, key="gen_btn"):
            if mode_key == "销售":
                info = f"产品：{product or '未填写'}\n行业：{target_industry or '未填写'}\n规模：{target_size or '未填写'}\n痛点：{pain_point or '未填写'}\n补充：{extra or '无'}"
                prompt_text = f"你是商业需求分析师。生成一段专业完整的需求描述（150-200字）。用户信息：\n{info}\n要求：直接输出描述，不要有其他内容。"
            else:
                info = f"技能：{skill or '未填写'}\n技术栈：{tech_stack or '未填写'}\n目标行业：{target_industry_job or '未填写'}\n职级：{job_level or '未填写'}\n补充：{extra or '无'}"
                prompt_text = f"你是职业规划师。生成一段专业完整的求职需求描述（150-200字）。用户信息：\n{info}\n要求：直接输出描述，不要有其他内容。"
            
            with st.spinner("🤖 AI 生成中..."):
                try:
                    resp = client.chat.completions.create(
                        model="deepseek-chat",
                        messages=[{"role": "system", "content": "你是专业文案助手。"}, {"role": "user", "content": prompt_text}],
                        temperature=0.7,
                        max_tokens=800
                    )
                    generated_text = resp.choices[0].message.content
                    st.session_state.generated_need = generated_text
                    
                    st.markdown("##### ✅ 生成结果：")
                    st.info(generated_text)
                    
                    if st.button("📥 填入输入框", use_container_width=True, key="fill_btn"):
                        # 直接修改 session_state 中 text_area 对应的 key
                        st.session_state.need_input = generated_text
                        st.success("✅ 已填入输入框！")
                        
                except Exception as e:
                    st.error(f"生成失败: {str(e)}")
    
    # ===== 需求输入框 =====
    # 初始化
    if 'need_input' not in st.session_state:
        st.session_state.need_input = ""
    
    # 用 key 直接绑定，不写 value
    st.text_area(
        "📝 描述你的需求",
        height=120,
        placeholder="示例：我销售AI客服系统，目标客户是电商和零售公司，有客服团队，最近有融资或扩张计划。",
        key="need_input"
    )
    
    if st.button("🔍 开始搜索", use_container_width=True, type="primary"):
        # 从 session_state 读取
        need_description = st.session_state.get("need_input", "")
        if not need_description:
            st.error("⚠️ 请先输入需求描述")
        else:
            result_df = quick_search(need_description, mode_key)
            if not result_df.empty:
                result_df = result_df.sort_values("综合评分", ascending=False)
                
                st.markdown("---")
                st.markdown(f"##### 📊 搜索结果 · 共 {len(result_df)} 家公司")
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("🏢 公司总数", len(result_df))
                with col2:
                    st.metric("🔥 高优先级", len(result_df[result_df['优先级'].str.contains('高')]))
                with col3:
                    st.metric("📊 平均评分", int(result_df['综合评分'].mean()))
                with col4:
                    st.metric("📡 数据源", len(result_df['数据来源'].unique()))
                
                st.markdown("---")
                
                for _, row in result_df.iterrows():
                    score = row['综合评分']
                    priority = row['优先级']
                    p_class = "priority-high" if "高" in str(priority) else "priority-mid" if "中" in str(priority) else "priority-low"
                    p_label = "🔥 高优先级" if "高" in str(priority) else "📌 中优先级" if "中" in str(priority) else "💤 低优先级"
                    
                    st.markdown(f"""
                    <div class="company-card">
                        <div style="display:flex;justify-content:space-between;align-items:center;">
                            <div><strong>{row['公司名称']}</strong> <span class="{p_class}">{p_label}</span></div>
                            <div><span style="font-size:24px;font-weight:700;color:#667eea;">{score}</span></div>
                        </div>
                        <div style="margin-top:6px;display:flex;flex-wrap:wrap;gap:4px;">
                            <span class="tag">🎯 匹配度: {row.get('匹配度', 'N/A')}</span>
                            <span class="tag">📡 {row.get('数据来源', '')}</span>
                            {f'<span class="tag">👤 {row["创始人"]}</span>' if row.get('创始人') else ''}
                            {f'<span class="tag">📅 {row["成立时间"]}</span>' if row.get('成立时间') else ''}
                            {f'<span class="tag">💼 {row["招聘数"]}个岗位</span>' if row.get('招聘数', 0) > 0 else ''}
                        </div>
                        <div style="margin-top:6px;font-size:14px;color:#3c4043;">{row.get('理由', '')[:100]}</div>
                        <div style="font-size:13px;color:#667eea;">💡 {row.get('建议动作', '')}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                csv = result_df.to_csv(index=False).encode('utf-8-sig')
                st.download_button("📥 下载结果 (CSV)", data=csv, file_name=f"觅镜_结果_{datetime.now().strftime('%Y%m%d')}.csv", mime="text/csv", use_container_width=True)# ============================================================
# TAB 1: 发现引擎（修复版）
# ============================================================
with tab_main:
    st.markdown("##### 选择使用场景")
    
    if 'mode_selected' not in st.session_state:
        st.session_state.mode_selected = "销售"
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💼 销售模式\n找潜在客户", use_container_width=True, key="mode_sales"):
            st.session_state.mode_selected = "销售"
            st.rerun()
    with col2:
        if st.button("🎓 求职模式\n找理想雇主", use_container_width=True, key="mode_job"):
            st.session_state.mode_selected = "求职"
            st.rerun()
    
    mode_key = st.session_state.mode_selected
    st.markdown(f'<div style="background:linear-gradient(135deg,#667eea,#764ba2);color:white;padding:10px 20px;border-radius:10px;text-align:center;font-weight:600;margin:8px 0 12px 0;">✅ 当前模式：{"💼 销售" if mode_key == "销售" else "🎓 求职"}</div>', unsafe_allow_html=True)
    
    # ===== AI 帮你写需求 =====
    with st.expander("🤖 AI 帮我写需求描述", expanded=False):
        st.caption("💡 填写信息后点击生成，AI 会自动生成需求描述，然后点击「填入输入框」")
        
        if mode_key == "销售":
            col_a, col_b = st.columns(2)
            with col_a:
                product = st.text_input("产品/服务", placeholder="AI客服系统", key="p1")
                target_industry = st.text_input("目标行业", placeholder="电商", key="p2")
            with col_b:
                target_size = st.text_input("目标规模", placeholder="500人以上", key="p3")
                pain_point = st.text_input("客户痛点", placeholder="客服响应慢", key="p4")
            extra = st.text_area("补充信息", placeholder="最近有融资的优先", key="p5", height=40)
        else:
            col_a, col_b = st.columns(2)
            with col_a:
                skill = st.text_input("核心技能", placeholder="前端开发", key="j1")
                tech_stack = st.text_input("技术栈", placeholder="React, TypeScript", key="j2")
            with col_b:
                target_industry_job = st.text_input("目标行业", placeholder="互联网", key="j3")
                job_level = st.text_input("目标职级", placeholder="中级", key="j4")
            extra = st.text_area("补充信息", placeholder="希望公司已盈利", key="j5", height=40)
        
        if st.button("🚀 生成需求描述", use_container_width=True, key="gen_btn"):
            if mode_key == "销售":
                info = f"产品：{product or '未填写'}\n行业：{target_industry or '未填写'}\n规模：{target_size or '未填写'}\n痛点：{pain_point or '未填写'}\n补充：{extra or '无'}"
                prompt_text = f"你是商业需求分析师。生成一段专业完整的需求描述（150-200字）。用户信息：\n{info}\n要求：直接输出描述，不要有其他内容。"
            else:
                info = f"技能：{skill or '未填写'}\n技术栈：{tech_stack or '未填写'}\n目标行业：{target_industry_job or '未填写'}\n职级：{job_level or '未填写'}\n补充：{extra or '无'}"
                prompt_text = f"你是职业规划师。生成一段专业完整的求职需求描述（150-200字）。用户信息：\n{info}\n要求：直接输出描述，不要有其他内容。"
            
            with st.spinner("🤖 AI 生成中..."):
                try:
                    resp = client.chat.completions.create(
                        model="deepseek-chat",
                        messages=[{"role": "system", "content": "你是专业文案助手。"}, {"role": "user", "content": prompt_text}],
                        temperature=0.7,
                        max_tokens=800
                    )
                    generated_text = resp.choices[0].message.content
                    st.session_state.generated_need = generated_text
                    
                    st.markdown("##### ✅ 生成结果：")
                    st.info(generated_text)
                    
                    if st.button("📥 填入输入框", use_container_width=True, key="fill_btn"):
                        # 直接修改 session_state 中 text_area 对应的 key
                        st.session_state.need_input = generated_text
                        st.success("✅ 已填入输入框！")
                        
                except Exception as e:
                    st.error(f"生成失败: {str(e)}")
    
    # ===== 需求输入框 =====
    # 初始化
    if 'need_input' not in st.session_state:
        st.session_state.need_input = ""
    
    # 用 key 直接绑定，不写 value
    st.text_area(
        "📝 描述你的需求",
        height=120,
        placeholder="示例：我销售AI客服系统，目标客户是电商和零售公司，有客服团队，最近有融资或扩张计划。",
        key="need_input"
    )
    
    if st.button("🔍 开始搜索", use_container_width=True, type="primary"):
        # 从 session_state 读取
        need_description = st.session_state.get("need_input", "")
        if not need_description:
            st.error("⚠️ 请先输入需求描述")
        else:
            result_df = quick_search(need_description, mode_key)
            if not result_df.empty:
                result_df = result_df.sort_values("综合评分", ascending=False)
                
                st.markdown("---")
                st.markdown(f"##### 📊 搜索结果 · 共 {len(result_df)} 家公司")
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("🏢 公司总数", len(result_df))
                with col2:
                    st.metric("🔥 高优先级", len(result_df[result_df['优先级'].str.contains('高')]))
                with col3:
                    st.metric("📊 平均评分", int(result_df['综合评分'].mean()))
                with col4:
                    st.metric("📡 数据源", len(result_df['数据来源'].unique()))
                
                st.markdown("---")
                
                for _, row in result_df.iterrows():
                    score = row['综合评分']
                    priority = row['优先级']
                    p_class = "priority-high" if "高" in str(priority) else "priority-mid" if "中" in str(priority) else "priority-low"
                    p_label = "🔥 高优先级" if "高" in str(priority) else "📌 中优先级" if "中" in str(priority) else "💤 低优先级"
                    
                    st.markdown(f"""
                    <div class="company-card">
                        <div style="display:flex;justify-content:space-between;align-items:center;">
                            <div><strong>{row['公司名称']}</strong> <span class="{p_class}">{p_label}</span></div>
                            <div><span style="font-size:24px;font-weight:700;color:#667eea;">{score}</span></div>
                        </div>
                        <div style="margin-top:6px;display:flex;flex-wrap:wrap;gap:4px;">
                            <span class="tag">🎯 匹配度: {row.get('匹配度', 'N/A')}</span>
                            <span class="tag">📡 {row.get('数据来源', '')}</span>
                            {f'<span class="tag">👤 {row["创始人"]}</span>' if row.get('创始人') else ''}
                            {f'<span class="tag">📅 {row["成立时间"]}</span>' if row.get('成立时间') else ''}
                            {f'<span class="tag">💼 {row["招聘数"]}个岗位</span>' if row.get('招聘数', 0) > 0 else ''}
                        </div>
                        <div style="margin-top:6px;font-size:14px;color:#3c4043;">{row.get('理由', '')[:100]}</div>
                        <div style="font-size:13px;color:#667eea;">💡 {row.get('建议动作', '')}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                csv = result_df.to_csv(index=False).encode('utf-8-sig')
                st.download_button("📥 下载结果 (CSV)", data=csv, file_name=f"觅镜_结果_{datetime.now().strftime('%Y%m%d')}.csv", mime="text/csv", use_container_width=True)# ============================================================
# TAB 1: 发现引擎（修复版）
# ============================================================
with tab_main:
    st.markdown("##### 选择使用场景")
    
    if 'mode_selected' not in st.session_state:
        st.session_state.mode_selected = "销售"
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💼 销售模式\n找潜在客户", use_container_width=True, key="mode_sales"):
            st.session_state.mode_selected = "销售"
            st.rerun()
    with col2:
        if st.button("🎓 求职模式\n找理想雇主", use_container_width=True, key="mode_job"):
            st.session_state.mode_selected = "求职"
            st.rerun()
    
    mode_key = st.session_state.mode_selected
    st.markdown(f'<div style="background:linear-gradient(135deg,#667eea,#764ba2);color:white;padding:10px 20px;border-radius:10px;text-align:center;font-weight:600;margin:8px 0 12px 0;">✅ 当前模式：{"💼 销售" if mode_key == "销售" else "🎓 求职"}</div>', unsafe_allow_html=True)
    
    # ===== AI 帮你写需求 =====
    with st.expander("🤖 AI 帮我写需求描述", expanded=False):
        st.caption("💡 填写信息后点击生成，AI 会自动生成需求描述，然后点击「填入输入框」")
        
        if mode_key == "销售":
            col_a, col_b = st.columns(2)
            with col_a:
                product = st.text_input("产品/服务", placeholder="AI客服系统", key="p1")
                target_industry = st.text_input("目标行业", placeholder="电商", key="p2")
            with col_b:
                target_size = st.text_input("目标规模", placeholder="500人以上", key="p3")
                pain_point = st.text_input("客户痛点", placeholder="客服响应慢", key="p4")
            extra = st.text_area("补充信息", placeholder="最近有融资的优先", key="p5", height=40)
        else:
            col_a, col_b = st.columns(2)
            with col_a:
                skill = st.text_input("核心技能", placeholder="前端开发", key="j1")
                tech_stack = st.text_input("技术栈", placeholder="React, TypeScript", key="j2")
            with col_b:
                target_industry_job = st.text_input("目标行业", placeholder="互联网", key="j3")
                job_level = st.text_input("目标职级", placeholder="中级", key="j4")
            extra = st.text_area("补充信息", placeholder="希望公司已盈利", key="j5", height=40)
        
        if st.button("🚀 生成需求描述", use_container_width=True, key="gen_btn"):
            if mode_key == "销售":
                info = f"产品：{product or '未填写'}\n行业：{target_industry or '未填写'}\n规模：{target_size or '未填写'}\n痛点：{pain_point or '未填写'}\n补充：{extra or '无'}"
                prompt_text = f"你是商业需求分析师。生成一段专业完整的需求描述（150-200字）。用户信息：\n{info}\n要求：直接输出描述，不要有其他内容。"
            else:
                info = f"技能：{skill or '未填写'}\n技术栈：{tech_stack or '未填写'}\n目标行业：{target_industry_job or '未填写'}\n职级：{job_level or '未填写'}\n补充：{extra or '无'}"
                prompt_text = f"你是职业规划师。生成一段专业完整的求职需求描述（150-200字）。用户信息：\n{info}\n要求：直接输出描述，不要有其他内容。"
            
            with st.spinner("🤖 AI 生成中..."):
                try:
                    resp = client.chat.completions.create(
                        model="deepseek-chat",
                        messages=[{"role": "system", "content": "你是专业文案助手。"}, {"role": "user", "content": prompt_text}],
                        temperature=0.7,
                        max_tokens=800
                    )
                    generated_text = resp.choices[0].message.content
                    st.session_state.generated_need = generated_text
                    
                    st.markdown("##### ✅ 生成结果：")
                    st.info(generated_text)
                    
                    if st.button("📥 填入输入框", use_container_width=True, key="fill_btn"):
                        # 直接修改 session_state 中 text_area 对应的 key
                        st.session_state.need_input = generated_text
                        st.success("✅ 已填入输入框！")
                        
                except Exception as e:
                    st.error(f"生成失败: {str(e)}")
    
    # ===== 需求输入框 =====
    # 初始化
    if 'need_input' not in st.session_state:
        st.session_state.need_input = ""
    
    # 用 key 直接绑定，不写 value
    st.text_area(
        "📝 描述你的需求",
        height=120,
        placeholder="示例：我销售AI客服系统，目标客户是电商和零售公司，有客服团队，最近有融资或扩张计划。",
        key="need_input"
    )
    
    if st.button("🔍 开始搜索", use_container_width=True, type="primary"):
        # 从 session_state 读取
        need_description = st.session_state.get("need_input", "")
        if not need_description:
            st.error("⚠️ 请先输入需求描述")
        else:
            result_df = quick_search(need_description, mode_key)
            if not result_df.empty:
                result_df = result_df.sort_values("综合评分", ascending=False)
                
                st.markdown("---")
                st.markdown(f"##### 📊 搜索结果 · 共 {len(result_df)} 家公司")
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("🏢 公司总数", len(result_df))
                with col2:
                    st.metric("🔥 高优先级", len(result_df[result_df['优先级'].str.contains('高')]))
                with col3:
                    st.metric("📊 平均评分", int(result_df['综合评分'].mean()))
                with col4:
                    st.metric("📡 数据源", len(result_df['数据来源'].unique()))
                
                st.markdown("---")
                
                for _, row in result_df.iterrows():
                    score = row['综合评分']
                    priority = row['优先级']
                    p_class = "priority-high" if "高" in str(priority) else "priority-mid" if "中" in str(priority) else "priority-low"
                    p_label = "🔥 高优先级" if "高" in str(priority) else "📌 中优先级" if "中" in str(priority) else "💤 低优先级"
                    
                    st.markdown(f"""
                    <div class="company-card">
                        <div style="display:flex;justify-content:space-between;align-items:center;">
                            <div><strong>{row['公司名称']}</strong> <span class="{p_class}">{p_label}</span></div>
                            <div><span style="font-size:24px;font-weight:700;color:#667eea;">{score}</span></div>
                        </div>
                        <div style="margin-top:6px;display:flex;flex-wrap:wrap;gap:4px;">
                            <span class="tag">🎯 匹配度: {row.get('匹配度', 'N/A')}</span>
                            <span class="tag">📡 {row.get('数据来源', '')}</span>
                            {f'<span class="tag">👤 {row["创始人"]}</span>' if row.get('创始人') else ''}
                            {f'<span class="tag">📅 {row["成立时间"]}</span>' if row.get('成立时间') else ''}
                            {f'<span class="tag">💼 {row["招聘数"]}个岗位</span>' if row.get('招聘数', 0) > 0 else ''}
                        </div>
                        <div style="margin-top:6px;font-size:14px;color:#3c4043;">{row.get('理由', '')[:100]}</div>
                        <div style="font-size:13px;color:#667eea;">💡 {row.get('建议动作', '')}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                csv = result_df.to_csv(index=False).encode('utf-8-sig')
                st.download_button("📥 下载结果 (CSV)", data=csv, file_name=f"觅镜_结果_{datetime.now().strftime('%Y%m%d')}.csv", mime="text/csv", use_container_width=True)# ============================================================
# TAB 1: 发现引擎（修复版）
# ============================================================
with tab_main:
    st.markdown("##### 选择使用场景")
    
    if 'mode_selected' not in st.session_state:
        st.session_state.mode_selected = "销售"
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💼 销售模式\n找潜在客户", use_container_width=True, key="mode_sales"):
            st.session_state.mode_selected = "销售"
            st.rerun()
    with col2:
        if st.button("🎓 求职模式\n找理想雇主", use_container_width=True, key="mode_job"):
            st.session_state.mode_selected = "求职"
            st.rerun()
    
    mode_key = st.session_state.mode_selected
    st.markdown(f'<div style="background:linear-gradient(135deg,#667eea,#764ba2);color:white;padding:10px 20px;border-radius:10px;text-align:center;font-weight:600;margin:8px 0 12px 0;">✅ 当前模式：{"💼 销售" if mode_key == "销售" else "🎓 求职"}</div>', unsafe_allow_html=True)
    
    # ===== AI 帮你写需求 =====
    with st.expander("🤖 AI 帮我写需求描述", expanded=False):
        st.caption("💡 填写信息后点击生成，AI 会自动生成需求描述，然后点击「填入输入框」")
        
        if mode_key == "销售":
            col_a, col_b = st.columns(2)
            with col_a:
                product = st.text_input("产品/服务", placeholder="AI客服系统", key="p1")
                target_industry = st.text_input("目标行业", placeholder="电商", key="p2")
            with col_b:
                target_size = st.text_input("目标规模", placeholder="500人以上", key="p3")
                pain_point = st.text_input("客户痛点", placeholder="客服响应慢", key="p4")
            extra = st.text_area("补充信息", placeholder="最近有融资的优先", key="p5", height=40)
        else:
            col_a, col_b = st.columns(2)
            with col_a:
                skill = st.text_input("核心技能", placeholder="前端开发", key="j1")
                tech_stack = st.text_input("技术栈", placeholder="React, TypeScript", key="j2")
            with col_b:
                target_industry_job = st.text_input("目标行业", placeholder="互联网", key="j3")
                job_level = st.text_input("目标职级", placeholder="中级", key="j4")
            extra = st.text_area("补充信息", placeholder="希望公司已盈利", key="j5", height=40)
        
        if st.button("🚀 生成需求描述", use_container_width=True, key="gen_btn"):
            if mode_key == "销售":
                info = f"产品：{product or '未填写'}\n行业：{target_industry or '未填写'}\n规模：{target_size or '未填写'}\n痛点：{pain_point or '未填写'}\n补充：{extra or '无'}"
                prompt_text = f"你是商业需求分析师。生成一段专业完整的需求描述（150-200字）。用户信息：\n{info}\n要求：直接输出描述，不要有其他内容。"
            else:
                info = f"技能：{skill or '未填写'}\n技术栈：{tech_stack or '未填写'}\n目标行业：{target_industry_job or '未填写'}\n职级：{job_level or '未填写'}\n补充：{extra or '无'}"
                prompt_text = f"你是职业规划师。生成一段专业完整的求职需求描述（150-200字）。用户信息：\n{info}\n要求：直接输出描述，不要有其他内容。"
            
            with st.spinner("🤖 AI 生成中..."):
                try:
                    resp = client.chat.completions.create(
                        model="deepseek-chat",
                        messages=[{"role": "system", "content": "你是专业文案助手。"}, {"role": "user", "content": prompt_text}],
                        temperature=0.7,
                        max_tokens=800
                    )
                    generated_text = resp.choices[0].message.content
                    st.session_state.generated_need = generated_text
                    
                    st.markdown("##### ✅ 生成结果：")
                    st.info(generated_text)
                    
                    if st.button("📥 填入输入框", use_container_width=True, key="fill_btn"):
                        # 直接修改 session_state 中 text_area 对应的 key
                        st.session_state.need_input = generated_text
                        st.success("✅ 已填入输入框！")
                        
                except Exception as e:
                    st.error(f"生成失败: {str(e)}")
    
    # ===== 需求输入框 =====
    # 初始化
    if 'need_input' not in st.session_state:
        st.session_state.need_input = ""
    
    # 用 key 直接绑定，不写 value
    st.text_area(
        "📝 描述你的需求",
        height=120,
        placeholder="示例：我销售AI客服系统，目标客户是电商和零售公司，有客服团队，最近有融资或扩张计划。",
        key="need_input"
    )
    
    if st.button("🔍 开始搜索", use_container_width=True, type="primary"):
        # 从 session_state 读取
        need_description = st.session_state.get("need_input", "")
        if not need_description:
            st.error("⚠️ 请先输入需求描述")
        else:
            result_df = quick_search(need_description, mode_key)
            if not result_df.empty:
                result_df = result_df.sort_values("综合评分", ascending=False)
                
                st.markdown("---")
                st.markdown(f"##### 📊 搜索结果 · 共 {len(result_df)} 家公司")
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("🏢 公司总数", len(result_df))
                with col2:
                    st.metric("🔥 高优先级", len(result_df[result_df['优先级'].str.contains('高')]))
                with col3:
                    st.metric("📊 平均评分", int(result_df['综合评分'].mean()))
                with col4:
                    st.metric("📡 数据源", len(result_df['数据来源'].unique()))
                
                st.markdown("---")
                
                for _, row in result_df.iterrows():
                    score = row['综合评分']
                    priority = row['优先级']
                    p_class = "priority-high" if "高" in str(priority) else "priority-mid" if "中" in str(priority) else "priority-low"
                    p_label = "🔥 高优先级" if "高" in str(priority) else "📌 中优先级" if "中" in str(priority) else "💤 低优先级"
                    
                    st.markdown(f"""
                    <div class="company-card">
                        <div style="display:flex;justify-content:space-between;align-items:center;">
                            <div><strong>{row['公司名称']}</strong> <span class="{p_class}">{p_label}</span></div>
                            <div><span style="font-size:24px;font-weight:700;color:#667eea;">{score}</span></div>
                        </div>
                        <div style="margin-top:6px;display:flex;flex-wrap:wrap;gap:4px;">
                            <span class="tag">🎯 匹配度: {row.get('匹配度', 'N/A')}</span>
                            <span class="tag">📡 {row.get('数据来源', '')}</span>
                            {f'<span class="tag">👤 {row["创始人"]}</span>' if row.get('创始人') else ''}
                            {f'<span class="tag">📅 {row["成立时间"]}</span>' if row.get('成立时间') else ''}
                            {f'<span class="tag">💼 {row["招聘数"]}个岗位</span>' if row.get('招聘数', 0) > 0 else ''}
                        </div>
                        <div style="margin-top:6px;font-size:14px;color:#3c4043;">{row.get('理由', '')[:100]}</div>
                        <div style="font-size:13px;color:#667eea;">💡 {row.get('建议动作', '')}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                csv = result_df.to_csv(index=False).encode('utf-8-sig')
                st.download_button("📥 下载结果 (CSV)", data=csv, file_name=f"觅镜_结果_{datetime.now().strftime('%Y%m%d')}.csv", mime="text/csv", use_container_width=True)# ============================================================
# TAB 1: 发现引擎（修复版）
# ============================================================
with tab_main:
    st.markdown("##### 选择使用场景")
    
    if 'mode_selected' not in st.session_state:
        st.session_state.mode_selected = "销售"
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💼 销售模式\n找潜在客户", use_container_width=True, key="mode_sales"):
            st.session_state.mode_selected = "销售"
            st.rerun()
    with col2:
        if st.button("🎓 求职模式\n找理想雇主", use_container_width=True, key="mode_job"):
            st.session_state.mode_selected = "求职"
            st.rerun()
    
    mode_key = st.session_state.mode_selected
    st.markdown(f'<div style="background:linear-gradient(135deg,#667eea,#764ba2);color:white;padding:10px 20px;border-radius:10px;text-align:center;font-weight:600;margin:8px 0 12px 0;">✅ 当前模式：{"💼 销售" if mode_key == "销售" else "🎓 求职"}</div>', unsafe_allow_html=True)
    
    # ===== AI 帮你写需求 =====
    with st.expander("🤖 AI 帮我写需求描述", expanded=False):
        st.caption("💡 填写信息后点击生成，AI 会自动生成需求描述，然后点击「填入输入框」")
        
        if mode_key == "销售":
            col_a, col_b = st.columns(2)
            with col_a:
                product = st.text_input("产品/服务", placeholder="AI客服系统", key="p1")
                target_industry = st.text_input("目标行业", placeholder="电商", key="p2")
            with col_b:
                target_size = st.text_input("目标规模", placeholder="500人以上", key="p3")
                pain_point = st.text_input("客户痛点", placeholder="客服响应慢", key="p4")
            extra = st.text_area("补充信息", placeholder="最近有融资的优先", key="p5", height=40)
        else:
            col_a, col_b = st.columns(2)
            with col_a:
                skill = st.text_input("核心技能", placeholder="前端开发", key="j1")
                tech_stack = st.text_input("技术栈", placeholder="React, TypeScript", key="j2")
            with col_b:
                target_industry_job = st.text_input("目标行业", placeholder="互联网", key="j3")
                job_level = st.text_input("目标职级", placeholder="中级", key="j4")
            extra = st.text_area("补充信息", placeholder="希望公司已盈利", key="j5", height=40)
        
        if st.button("🚀 生成需求描述", use_container_width=True, key="gen_btn"):
            if mode_key == "销售":
                info = f"产品：{product or '未填写'}\n行业：{target_industry or '未填写'}\n规模：{target_size or '未填写'}\n痛点：{pain_point or '未填写'}\n补充：{extra or '无'}"
                prompt_text = f"你是商业需求分析师。生成一段专业完整的需求描述（150-200字）。用户信息：\n{info}\n要求：直接输出描述，不要有其他内容。"
            else:
                info = f"技能：{skill or '未填写'}\n技术栈：{tech_stack or '未填写'}\n目标行业：{target_industry_job or '未填写'}\n职级：{job_level or '未填写'}\n补充：{extra or '无'}"
                prompt_text = f"你是职业规划师。生成一段专业完整的求职需求描述（150-200字）。用户信息：\n{info}\n要求：直接输出描述，不要有其他内容。"
            
            with st.spinner("🤖 AI 生成中..."):
                try:
                    resp = client.chat.completions.create(
                        model="deepseek-chat",
                        messages=[{"role": "system", "content": "你是专业文案助手。"}, {"role": "user", "content": prompt_text}],
                        temperature=0.7,
                        max_tokens=800
                    )
                    generated_text = resp.choices[0].message.content
                    st.session_state.generated_need = generated_text
                    
                    st.markdown("##### ✅ 生成结果：")
                    st.info(generated_text)
                    
                    if st.button("📥 填入输入框", use_container_width=True, key="fill_btn"):
                        # 直接修改 session_state 中 text_area 对应的 key
                        st.session_state.need_input = generated_text
                        st.success("✅ 已填入输入框！")
                        
                except Exception as e:
                    st.error(f"生成失败: {str(e)}")
    
    # ===== 需求输入框 =====
    # 初始化
    if 'need_input' not in st.session_state:
        st.session_state.need_input = ""
    
    # 用 key 直接绑定，不写 value
    st.text_area(
        "📝 描述你的需求",
        height=120,
        placeholder="示例：我销售AI客服系统，目标客户是电商和零售公司，有客服团队，最近有融资或扩张计划。",
        key="need_input"
    )
    
    if st.button("🔍 开始搜索", use_container_width=True, type="primary"):
        # 从 session_state 读取
        need_description = st.session_state.get("need_input", "")
        if not need_description:
            st.error("⚠️ 请先输入需求描述")
        else:
            result_df = quick_search(need_description, mode_key)
            if not result_df.empty:
                result_df = result_df.sort_values("综合评分", ascending=False)
                
                st.markdown("---")
                st.markdown(f"##### 📊 搜索结果 · 共 {len(result_df)} 家公司")
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("🏢 公司总数", len(result_df))
                with col2:
                    st.metric("🔥 高优先级", len(result_df[result_df['优先级'].str.contains('高')]))
                with col3:
                    st.metric("📊 平均评分", int(result_df['综合评分'].mean()))
                with col4:
                    st.metric("📡 数据源", len(result_df['数据来源'].unique()))
                
                st.markdown("---")
                
                for _, row in result_df.iterrows():
                    score = row['综合评分']
                    priority = row['优先级']
                    p_class = "priority-high" if "高" in str(priority) else "priority-mid" if "中" in str(priority) else "priority-low"
                    p_label = "🔥 高优先级" if "高" in str(priority) else "📌 中优先级" if "中" in str(priority) else "💤 低优先级"
                    
                    st.markdown(f"""
                    <div class="company-card">
                        <div style="display:flex;justify-content:space-between;align-items:center;">
                            <div><strong>{row['公司名称']}</strong> <span class="{p_class}">{p_label}</span></div>
                            <div><span style="font-size:24px;font-weight:700;color:#667eea;">{score}</span></div>
                        </div>
                        <div style="margin-top:6px;display:flex;flex-wrap:wrap;gap:4px;">
                            <span class="tag">🎯 匹配度: {row.get('匹配度', 'N/A')}</span>
                            <span class="tag">📡 {row.get('数据来源', '')}</span>
                            {f'<span class="tag">👤 {row["创始人"]}</span>' if row.get('创始人') else ''}
                            {f'<span class="tag">📅 {row["成立时间"]}</span>' if row.get('成立时间') else ''}
                            {f'<span class="tag">💼 {row["招聘数"]}个岗位</span>' if row.get('招聘数', 0) > 0 else ''}
                        </div>
                        <div style="margin-top:6px;font-size:14px;color:#3c4043;">{row.get('理由', '')[:100]}</div>
                        <div style="font-size:13px;color:#667eea;">💡 {row.get('建议动作', '')}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                csv = result_df.to_csv(index=False).encode('utf-8-sig')
                st.download_button("📥 下载结果 (CSV)", data=csv, file_name=f"觅镜_结果_{datetime.now().strftime('%Y%m%d')}.csv", mime="text/csv", use_container_width=True)# ============================================================
# TAB 1: 发现引擎（修复版）
# ============================================================
with tab_main:
    st.markdown("##### 选择使用场景")
    
    if 'mode_selected' not in st.session_state:
        st.session_state.mode_selected = "销售"
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💼 销售模式\n找潜在客户", use_container_width=True, key="mode_sales"):
            st.session_state.mode_selected = "销售"
            st.rerun()
    with col2:
        if st.button("🎓 求职模式\n找理想雇主", use_container_width=True, key="mode_job"):
            st.session_state.mode_selected = "求职"
            st.rerun()
    
    mode_key = st.session_state.mode_selected
    st.markdown(f'<div style="background:linear-gradient(135deg,#667eea,#764ba2);color:white;padding:10px 20px;border-radius:10px;text-align:center;font-weight:600;margin:8px 0 12px 0;">✅ 当前模式：{"💼 销售" if mode_key == "销售" else "🎓 求职"}</div>', unsafe_allow_html=True)
    
    # ===== AI 帮你写需求 =====
    with st.expander("🤖 AI 帮我写需求描述", expanded=False):
        st.caption("💡 填写信息后点击生成，AI 会自动生成需求描述，然后点击「填入输入框」")
        
        if mode_key == "销售":
            col_a, col_b = st.columns(2)
            with col_a:
                product = st.text_input("产品/服务", placeholder="AI客服系统", key="p1")
                target_industry = st.text_input("目标行业", placeholder="电商", key="p2")
            with col_b:
                target_size = st.text_input("目标规模", placeholder="500人以上", key="p3")
                pain_point = st.text_input("客户痛点", placeholder="客服响应慢", key="p4")
            extra = st.text_area("补充信息", placeholder="最近有融资的优先", key="p5", height=40)
        else:
            col_a, col_b = st.columns(2)
            with col_a:
                skill = st.text_input("核心技能", placeholder="前端开发", key="j1")
                tech_stack = st.text_input("技术栈", placeholder="React, TypeScript", key="j2")
            with col_b:
                target_industry_job = st.text_input("目标行业", placeholder="互联网", key="j3")
                job_level = st.text_input("目标职级", placeholder="中级", key="j4")
            extra = st.text_area("补充信息", placeholder="希望公司已盈利", key="j5", height=40)
        
        if st.button("🚀 生成需求描述", use_container_width=True, key="gen_btn"):
            if mode_key == "销售":
                info = f"产品：{product or '未填写'}\n行业：{target_industry or '未填写'}\n规模：{target_size or '未填写'}\n痛点：{pain_point or '未填写'}\n补充：{extra or '无'}"
                prompt_text = f"你是商业需求分析师。生成一段专业完整的需求描述（150-200字）。用户信息：\n{info}\n要求：直接输出描述，不要有其他内容。"
            else:
                info = f"技能：{skill or '未填写'}\n技术栈：{tech_stack or '未填写'}\n目标行业：{target_industry_job or '未填写'}\n职级：{job_level or '未填写'}\n补充：{extra or '无'}"
                prompt_text = f"你是职业规划师。生成一段专业完整的求职需求描述（150-200字）。用户信息：\n{info}\n要求：直接输出描述，不要有其他内容。"
            
            with st.spinner("🤖 AI 生成中..."):
                try:
                    resp = client.chat.completions.create(
                        model="deepseek-chat",
                        messages=[{"role": "system", "content": "你是专业文案助手。"}, {"role": "user", "content": prompt_text}],
                        temperature=0.7,
                        max_tokens=800
                    )
                    generated_text = resp.choices[0].message.content
                    st.session_state.generated_need = generated_text
                    
                    st.markdown("##### ✅ 生成结果：")
                    st.info(generated_text)
                    
                    if st.button("📥 填入输入框", use_container_width=True, key="fill_btn"):
                        # 直接修改 session_state 中 text_area 对应的 key
                        st.session_state.need_input = generated_text
                        st.success("✅ 已填入输入框！")
                        
                except Exception as e:
                    st.error(f"生成失败: {str(e)}")
    
    # ===== 需求输入框 =====
    # 初始化
    if 'need_input' not in st.session_state:
        st.session_state.need_input = ""
    
    # 用 key 直接绑定，不写 value
    st.text_area(
        "📝 描述你的需求",
        height=120,
        placeholder="示例：我销售AI客服系统，目标客户是电商和零售公司，有客服团队，最近有融资或扩张计划。",
        key="need_input"
    )
    
    if st.button("🔍 开始搜索", use_container_width=True, type="primary"):
        # 从 session_state 读取
        need_description = st.session_state.get("need_input", "")
        if not need_description:
            st.error("⚠️ 请先输入需求描述")
        else:
            result_df = quick_search(need_description, mode_key)
            if not result_df.empty:
                result_df = result_df.sort_values("综合评分", ascending=False)
                
                st.markdown("---")
                st.markdown(f"##### 📊 搜索结果 · 共 {len(result_df)} 家公司")
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("🏢 公司总数", len(result_df))
                with col2:
                    st.metric("🔥 高优先级", len(result_df[result_df['优先级'].str.contains('高')]))
                with col3:
                    st.metric("📊 平均评分", int(result_df['综合评分'].mean()))
                with col4:
                    st.metric("📡 数据源", len(result_df['数据来源'].unique()))
                
                st.markdown("---")
                
                for _, row in result_df.iterrows():
                    score = row['综合评分']
                    priority = row['优先级']
                    p_class = "priority-high" if "高" in str(priority) else "priority-mid" if "中" in str(priority) else "priority-low"
                    p_label = "🔥 高优先级" if "高" in str(priority) else "📌 中优先级" if "中" in str(priority) else "💤 低优先级"
                    
                    st.markdown(f"""
                    <div class="company-card">
                        <div style="display:flex;justify-content:space-between;align-items:center;">
                            <div><strong>{row['公司名称']}</strong> <span class="{p_class}">{p_label}</span></div>
                            <div><span style="font-size:24px;font-weight:700;color:#667eea;">{score}</span></div>
                        </div>
                        <div style="margin-top:6px;display:flex;flex-wrap:wrap;gap:4px;">
                            <span class="tag">🎯 匹配度: {row.get('匹配度', 'N/A')}</span>
                            <span class="tag">📡 {row.get('数据来源', '')}</span>
                            {f'<span class="tag">👤 {row["创始人"]}</span>' if row.get('创始人') else ''}
                            {f'<span class="tag">📅 {row["成立时间"]}</span>' if row.get('成立时间') else ''}
                            {f'<span class="tag">💼 {row["招聘数"]}个岗位</span>' if row.get('招聘数', 0) > 0 else ''}
                        </div>
                        <div style="margin-top:6px;font-size:14px;color:#3c4043;">{row.get('理由', '')[:100]}</div>
                        <div style="font-size:13px;color:#667eea;">💡 {row.get('建议动作', '')}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                csv = result_df.to_csv(index=False).encode('utf-8-sig')
                st.download_button("📥 下载结果 (CSV)", data=csv, file_name=f"觅镜_结果_{datetime.now().strftime('%Y%m%d')}.csv", mime="text/csv", use_container_width=True)# ============================================================
# TAB 1: 发现引擎（修复版）
# ============================================================
with tab_main:
    st.markdown("##### 选择使用场景")
    
    if 'mode_selected' not in st.session_state:
        st.session_state.mode_selected = "销售"
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💼 销售模式\n找潜在客户", use_container_width=True, key="mode_sales"):
            st.session_state.mode_selected = "销售"
            st.rerun()
    with col2:
        if st.button("🎓 求职模式\n找理想雇主", use_container_width=True, key="mode_job"):
            st.session_state.mode_selected = "求职"
            st.rerun()
    
    mode_key = st.session_state.mode_selected
    st.markdown(f'<div style="background:linear-gradient(135deg,#667eea,#764ba2);color:white;padding:10px 20px;border-radius:10px;text-align:center;font-weight:600;margin:8px 0 12px 0;">✅ 当前模式：{"💼 销售" if mode_key == "销售" else "🎓 求职"}</div>', unsafe_allow_html=True)
    
    # ===== AI 帮你写需求 =====
    with st.expander("🤖 AI 帮我写需求描述", expanded=False):
        st.caption("💡 填写信息后点击生成，AI 会自动生成需求描述，然后点击「填入输入框」")
        
        if mode_key == "销售":
            col_a, col_b = st.columns(2)
            with col_a:
                product = st.text_input("产品/服务", placeholder="AI客服系统", key="p1")
                target_industry = st.text_input("目标行业", placeholder="电商", key="p2")
            with col_b:
                target_size = st.text_input("目标规模", placeholder="500人以上", key="p3")
                pain_point = st.text_input("客户痛点", placeholder="客服响应慢", key="p4")
            extra = st.text_area("补充信息", placeholder="最近有融资的优先", key="p5", height=40)
        else:
            col_a, col_b = st.columns(2)
            with col_a:
                skill = st.text_input("核心技能", placeholder="前端开发", key="j1")
                tech_stack = st.text_input("技术栈", placeholder="React, TypeScript", key="j2")
            with col_b:
                target_industry_job = st.text_input("目标行业", placeholder="互联网", key="j3")
                job_level = st.text_input("目标职级", placeholder="中级", key="j4")
            extra = st.text_area("补充信息", placeholder="希望公司已盈利", key="j5", height=40)
        
        if st.button("🚀 生成需求描述", use_container_width=True, key="gen_btn"):
            if mode_key == "销售":
                info = f"产品：{product or '未填写'}\n行业：{target_industry or '未填写'}\n规模：{target_size or '未填写'}\n痛点：{pain_point or '未填写'}\n补充：{extra or '无'}"
                prompt_text = f"你是商业需求分析师。生成一段专业完整的需求描述（150-200字）。用户信息：\n{info}\n要求：直接输出描述，不要有其他内容。"
            else:
                info = f"技能：{skill or '未填写'}\n技术栈：{tech_stack or '未填写'}\n目标行业：{target_industry_job or '未填写'}\n职级：{job_level or '未填写'}\n补充：{extra or '无'}"
                prompt_text = f"你是职业规划师。生成一段专业完整的求职需求描述（150-200字）。用户信息：\n{info}\n要求：直接输出描述，不要有其他内容。"
            
            with st.spinner("🤖 AI 生成中..."):
                try:
                    resp = client.chat.completions.create(
                        model="deepseek-chat",
                        messages=[{"role": "system", "content": "你是专业文案助手。"}, {"role": "user", "content": prompt_text}],
                        temperature=0.7,
                        max_tokens=800
                    )
                    generated_text = resp.choices[0].message.content
                    st.session_state.generated_need = generated_text
                    
                    st.markdown("##### ✅ 生成结果：")
                    st.info(generated_text)
                    
                    if st.button("📥 填入输入框", use_container_width=True, key="fill_btn"):
                        # 直接修改 session_state 中 text_area 对应的 key
                        st.session_state.need_input = generated_text
                        st.success("✅ 已填入输入框！")
                        
                except Exception as e:
                    st.error(f"生成失败: {str(e)}")
    
    # ===== 需求输入框 =====
    # 初始化
    if 'need_input' not in st.session_state:
        st.session_state.need_input = ""
    
    # 用 key 直接绑定，不写 value
    st.text_area(
        "📝 描述你的需求",
        height=120,
        placeholder="示例：我销售AI客服系统，目标客户是电商和零售公司，有客服团队，最近有融资或扩张计划。",
        key="need_input"
    )
    
    if st.button("🔍 开始搜索", use_container_width=True, type="primary"):
        # 从 session_state 读取
        need_description = st.session_state.get("need_input", "")
        if not need_description:
            st.error("⚠️ 请先输入需求描述")
        else:
            result_df = quick_search(need_description, mode_key)
            if not result_df.empty:
                result_df = result_df.sort_values("综合评分", ascending=False)
                
                st.markdown("---")
                st.markdown(f"##### 📊 搜索结果 · 共 {len(result_df)} 家公司")
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("🏢 公司总数", len(result_df))
                with col2:
                    st.metric("🔥 高优先级", len(result_df[result_df['优先级'].str.contains('高')]))
                with col3:
                    st.metric("📊 平均评分", int(result_df['综合评分'].mean()))
                with col4:
                    st.metric("📡 数据源", len(result_df['数据来源'].unique()))
                
                st.markdown("---")
                
                for _, row in result_df.iterrows():
                    score = row['综合评分']
                    priority = row['优先级']
                    p_class = "priority-high" if "高" in str(priority) else "priority-mid" if "中" in str(priority) else "priority-low"
                    p_label = "🔥 高优先级" if "高" in str(priority) else "📌 中优先级" if "中" in str(priority) else "💤 低优先级"
                    
                    st.markdown(f"""
                    <div class="company-card">
                        <div style="display:flex;justify-content:space-between;align-items:center;">
                            <div><strong>{row['公司名称']}</strong> <span class="{p_class}">{p_label}</span></div>
                            <div><span style="font-size:24px;font-weight:700;color:#667eea;">{score}</span></div>
                        </div>
                        <div style="margin-top:6px;display:flex;flex-wrap:wrap;gap:4px;">
                            <span class="tag">🎯 匹配度: {row.get('匹配度', 'N/A')}</span>
                            <span class="tag">📡 {row.get('数据来源', '')}</span>
                            {f'<span class="tag">👤 {row["创始人"]}</span>' if row.get('创始人') else ''}
                            {f'<span class="tag">📅 {row["成立时间"]}</span>' if row.get('成立时间') else ''}
                            {f'<span class="tag">💼 {row["招聘数"]}个岗位</span>' if row.get('招聘数', 0) > 0 else ''}
                        </div>
                        <div style="margin-top:6px;font-size:14px;color:#3c4043;">{row.get('理由', '')[:100]}</div>
                        <div style="font-size:13px;color:#667eea;">💡 {row.get('建议动作', '')}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                csv = result_df.to_csv(index=False).encode('utf-8-sig')
                st.download_button("📥 下载结果 (CSV)", data=csv, file_name=f"觅镜_结果_{datetime.now().strftime('%Y%m%d')}.csv", mime="text/csv", use_container_width=True)# ============================================================
# TAB 1: 发现引擎（修复版）
# ============================================================
with tab_main:
    st.markdown("##### 选择使用场景")
    
    if 'mode_selected' not in st.session_state:
        st.session_state.mode_selected = "销售"
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💼 销售模式\n找潜在客户", use_container_width=True, key="mode_sales"):
            st.session_state.mode_selected = "销售"
            st.rerun()
    with col2:
        if st.button("🎓 求职模式\n找理想雇主", use_container_width=True, key="mode_job"):
            st.session_state.mode_selected = "求职"
            st.rerun()
    
    mode_key = st.session_state.mode_selected
    st.markdown(f'<div style="background:linear-gradient(135deg,#667eea,#764ba2);color:white;padding:10px 20px;border-radius:10px;text-align:center;font-weight:600;margin:8px 0 12px 0;">✅ 当前模式：{"💼 销售" if mode_key == "销售" else "🎓 求职"}</div>', unsafe_allow_html=True)
    
    # ===== AI 帮你写需求 =====
    with st.expander("🤖 AI 帮我写需求描述", expanded=False):
        st.caption("💡 填写信息后点击生成，AI 会自动生成需求描述，然后点击「填入输入框」")
        
        if mode_key == "销售":
            col_a, col_b = st.columns(2)
            with col_a:
                product = st.text_input("产品/服务", placeholder="AI客服系统", key="p1")
                target_industry = st.text_input("目标行业", placeholder="电商", key="p2")
            with col_b:
                target_size = st.text_input("目标规模", placeholder="500人以上", key="p3")
                pain_point = st.text_input("客户痛点", placeholder="客服响应慢", key="p4")
            extra = st.text_area("补充信息", placeholder="最近有融资的优先", key="p5", height=40)
        else:
            col_a, col_b = st.columns(2)
            with col_a:
                skill = st.text_input("核心技能", placeholder="前端开发", key="j1")
                tech_stack = st.text_input("技术栈", placeholder="React, TypeScript", key="j2")
            with col_b:
                target_industry_job = st.text_input("目标行业", placeholder="互联网", key="j3")
                job_level = st.text_input("目标职级", placeholder="中级", key="j4")
            extra = st.text_area("补充信息", placeholder="希望公司已盈利", key="j5", height=40)
        
        if st.button("🚀 生成需求描述", use_container_width=True, key="gen_btn"):
            if mode_key == "销售":
                info = f"产品：{product or '未填写'}\n行业：{target_industry or '未填写'}\n规模：{target_size or '未填写'}\n痛点：{pain_point or '未填写'}\n补充：{extra or '无'}"
                prompt_text = f"你是商业需求分析师。生成一段专业完整的需求描述（150-200字）。用户信息：\n{info}\n要求：直接输出描述，不要有其他内容。"
            else:
                info = f"技能：{skill or '未填写'}\n技术栈：{tech_stack or '未填写'}\n目标行业：{target_industry_job or '未填写'}\n职级：{job_level or '未填写'}\n补充：{extra or '无'}"
                prompt_text = f"你是职业规划师。生成一段专业完整的求职需求描述（150-200字）。用户信息：\n{info}\n要求：直接输出描述，不要有其他内容。"
            
            with st.spinner("🤖 AI 生成中..."):
                try:
                    resp = client.chat.completions.create(
                        model="deepseek-chat",
                        messages=[{"role": "system", "content": "你是专业文案助手。"}, {"role": "user", "content": prompt_text}],
                        temperature=0.7,
                        max_tokens=800
                    )
                    generated_text = resp.choices[0].message.content
                    st.session_state.generated_need = generated_text
                    
                    st.markdown("##### ✅ 生成结果：")
                    st.info(generated_text)
                    
                    if st.button("📥 填入输入框", use_container_width=True, key="fill_btn"):
                        # 直接修改 session_state 中 text_area 对应的 key
                        st.session_state.need_input = generated_text
                        st.success("✅ 已填入输入框！")
                        
                except Exception as e:
                    st.error(f"生成失败: {str(e)}")
    
    # ===== 需求输入框 =====
    # 初始化
    if 'need_input' not in st.session_state:
        st.session_state.need_input = ""
    
    # 用 key 直接绑定，不写 value
    st.text_area(
        "📝 描述你的需求",
        height=120,
        placeholder="示例：我销售AI客服系统，目标客户是电商和零售公司，有客服团队，最近有融资或扩张计划。",
        key="need_input"
    )
    
    if st.button("🔍 开始搜索", use_container_width=True, type="primary"):
        # 从 session_state 读取
        need_description = st.session_state.get("need_input", "")
        if not need_description:
            st.error("⚠️ 请先输入需求描述")
        else:
            result_df = quick_search(need_description, mode_key)
            if not result_df.empty:
                result_df = result_df.sort_values("综合评分", ascending=False)
                
                st.markdown("---")
                st.markdown(f"##### 📊 搜索结果 · 共 {len(result_df)} 家公司")
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("🏢 公司总数", len(result_df))
                with col2:
                    st.metric("🔥 高优先级", len(result_df[result_df['优先级'].str.contains('高')]))
                with col3:
                    st.metric("📊 平均评分", int(result_df['综合评分'].mean()))
                with col4:
                    st.metric("📡 数据源", len(result_df['数据来源'].unique()))
                
                st.markdown("---")
                
                for _, row in result_df.iterrows():
                    score = row['综合评分']
                    priority = row['优先级']
                    p_class = "priority-high" if "高" in str(priority) else "priority-mid" if "中" in str(priority) else "priority-low"
                    p_label = "🔥 高优先级" if "高" in str(priority) else "📌 中优先级" if "中" in str(priority) else "💤 低优先级"
                    
                    st.markdown(f"""
                    <div class="company-card">
                        <div style="display:flex;justify-content:space-between;align-items:center;">
                            <div><strong>{row['公司名称']}</strong> <span class="{p_class}">{p_label}</span></div>
                            <div><span style="font-size:24px;font-weight:700;color:#667eea;">{score}</span></div>
                        </div>
                        <div style="margin-top:6px;display:flex;flex-wrap:wrap;gap:4px;">
                            <span class="tag">🎯 匹配度: {row.get('匹配度', 'N/A')}</span>
                            <span class="tag">📡 {row.get('数据来源', '')}</span>
                            {f'<span class="tag">👤 {row["创始人"]}</span>' if row.get('创始人') else ''}
                            {f'<span class="tag">📅 {row["成立时间"]}</span>' if row.get('成立时间') else ''}
                            {f'<span class="tag">💼 {row["招聘数"]}个岗位</span>' if row.get('招聘数', 0) > 0 else ''}
                        </div>
                        <div style="margin-top:6px;font-size:14px;color:#3c4043;">{row.get('理由', '')[:100]}</div>
                        <div style="font-size:13px;color:#667eea;">💡 {row.get('建议动作', '')}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                csv = result_df.to_csv(index=False).encode('utf-8-sig')
                st.download_button("📥 下载结果 (CSV)", data=csv, file_name=f"觅镜_结果_{datetime.now().strftime('%Y%m%d')}.csv", mime="text/csv", use_container_width=True)# ============================================================
# TAB 1: 发现引擎（修复版）
# ============================================================
with tab_main:
    st.markdown("##### 选择使用场景")
    
    if 'mode_selected' not in st.session_state:
        st.session_state.mode_selected = "销售"
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💼 销售模式\n找潜在客户", use_container_width=True, key="mode_sales"):
            st.session_state.mode_selected = "销售"
            st.rerun()
    with col2:
        if st.button("🎓 求职模式\n找理想雇主", use_container_width=True, key="mode_job"):
            st.session_state.mode_selected = "求职"
            st.rerun()
    
    mode_key = st.session_state.mode_selected
    st.markdown(f'<div style="background:linear-gradient(135deg,#667eea,#764ba2);color:white;padding:10px 20px;border-radius:10px;text-align:center;font-weight:600;margin:8px 0 12px 0;">✅ 当前模式：{"💼 销售" if mode_key == "销售" else "🎓 求职"}</div>', unsafe_allow_html=True)
    
    # ===== AI 帮你写需求 =====
    with st.expander("🤖 AI 帮我写需求描述", expanded=False):
        st.caption("💡 填写信息后点击生成，AI 会自动生成需求描述，然后点击「填入输入框」")
        
        if mode_key == "销售":
            col_a, col_b = st.columns(2)
            with col_a:
                product = st.text_input("产品/服务", placeholder="AI客服系统", key="p1")
                target_industry = st.text_input("目标行业", placeholder="电商", key="p2")
            with col_b:
                target_size = st.text_input("目标规模", placeholder="500人以上", key="p3")
                pain_point = st.text_input("客户痛点", placeholder="客服响应慢", key="p4")
            extra = st.text_area("补充信息", placeholder="最近有融资的优先", key="p5", height=40)
        else:
            col_a, col_b = st.columns(2)
            with col_a:
                skill = st.text_input("核心技能", placeholder="前端开发", key="j1")
                tech_stack = st.text_input("技术栈", placeholder="React, TypeScript", key="j2")
            with col_b:
                target_industry_job = st.text_input("目标行业", placeholder="互联网", key="j3")
                job_level = st.text_input("目标职级", placeholder="中级", key="j4")
            extra = st.text_area("补充信息", placeholder="希望公司已盈利", key="j5", height=40)
        
        if st.button("🚀 生成需求描述", use_container_width=True, key="gen_btn"):
            if mode_key == "销售":
                info = f"产品：{product or '未填写'}\n行业：{target_industry or '未填写'}\n规模：{target_size or '未填写'}\n痛点：{pain_point or '未填写'}\n补充：{extra or '无'}"
                prompt_text = f"你是商业需求分析师。生成一段专业完整的需求描述（150-200字）。用户信息：\n{info}\n要求：直接输出描述，不要有其他内容。"
            else:
                info = f"技能：{skill or '未填写'}\n技术栈：{tech_stack or '未填写'}\n目标行业：{target_industry_job or '未填写'}\n职级：{job_level or '未填写'}\n补充：{extra or '无'}"
                prompt_text = f"你是职业规划师。生成一段专业完整的求职需求描述（150-200字）。用户信息：\n{info}\n要求：直接输出描述，不要有其他内容。"
            
            with st.spinner("🤖 AI 生成中..."):
                try:
                    resp = client.chat.completions.create(
                        model="deepseek-chat",
                        messages=[{"role": "system", "content": "你是专业文案助手。"}, {"role": "user", "content": prompt_text}],
                        temperature=0.7,
                        max_tokens=800
                    )
                    generated_text = resp.choices[0].message.content
                    st.session_state.generated_need = generated_text
                    
                    st.markdown("##### ✅ 生成结果：")
                    st.info(generated_text)
                    
                    if st.button("📥 填入输入框", use_container_width=True, key="fill_btn"):
                        # 直接修改 session_state 中 text_area 对应的 key
                        st.session_state.need_input = generated_text
                        st.success("✅ 已填入输入框！")
                        
                except Exception as e:
                    st.error(f"生成失败: {str(e)}")
    
    # ===== 需求输入框 =====
    # 初始化
    if 'need_input' not in st.session_state:
        st.session_state.need_input = ""
    
    # 用 key 直接绑定，不写 value
    st.text_area(
        "📝 描述你的需求",
        height=120,
        placeholder="示例：我销售AI客服系统，目标客户是电商和零售公司，有客服团队，最近有融资或扩张计划。",
        key="need_input"
    )
    
    if st.button("🔍 开始搜索", use_container_width=True, type="primary"):
        # 从 session_state 读取
        need_description = st.session_state.get("need_input", "")
        if not need_description:
            st.error("⚠️ 请先输入需求描述")
        else:
            result_df = quick_search(need_description, mode_key)
            if not result_df.empty:
                result_df = result_df.sort_values("综合评分", ascending=False)
                
                st.markdown("---")
                st.markdown(f"##### 📊 搜索结果 · 共 {len(result_df)} 家公司")
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("🏢 公司总数", len(result_df))
                with col2:
                    st.metric("🔥 高优先级", len(result_df[result_df['优先级'].str.contains('高')]))
                with col3:
                    st.metric("📊 平均评分", int(result_df['综合评分'].mean()))
                with col4:
                    st.metric("📡 数据源", len(result_df['数据来源'].unique()))
                
                st.markdown("---")
                
                for _, row in result_df.iterrows():
                    score = row['综合评分']
                    priority = row['优先级']
                    p_class = "priority-high" if "高" in str(priority) else "priority-mid" if "中" in str(priority) else "priority-low"
                    p_label = "🔥 高优先级" if "高" in str(priority) else "📌 中优先级" if "中" in str(priority) else "💤 低优先级"
                    
                    st.markdown(f"""
                    <div class="company-card">
                        <div style="display:flex;justify-content:space-between;align-items:center;">
                            <div><strong>{row['公司名称']}</strong> <span class="{p_class}">{p_label}</span></div>
                            <div><span style="font-size:24px;font-weight:700;color:#667eea;">{score}</span></div>
                        </div>
                        <div style="margin-top:6px;display:flex;flex-wrap:wrap;gap:4px;">
                            <span class="tag">🎯 匹配度: {row.get('匹配度', 'N/A')}</span>
                            <span class="tag">📡 {row.get('数据来源', '')}</span>
                            {f'<span class="tag">👤 {row["创始人"]}</span>' if row.get('创始人') else ''}
                            {f'<span class="tag">📅 {row["成立时间"]}</span>' if row.get('成立时间') else ''}
                            {f'<span class="tag">💼 {row["招聘数"]}个岗位</span>' if row.get('招聘数', 0) > 0 else ''}
                        </div>
                        <div style="margin-top:6px;font-size:14px;color:#3c4043;">{row.get('理由', '')[:100]}</div>
                        <div style="font-size:13px;color:#667eea;">💡 {row.get('建议动作', '')}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                csv = result_df.to_csv(index=False).encode('utf-8-sig')
                st.download_button("📥 下载结果 (CSV)", data=csv, file_name=f"觅镜_结果_{datetime.now().strftime('%Y%m%d')}.csv", mime="text/csv", use_container_width=True)# ============================================================
# TAB 1: 发现引擎（修复版）
# ============================================================
with tab_main:
    st.markdown("##### 选择使用场景")
    
    if 'mode_selected' not in st.session_state:
        st.session_state.mode_selected = "销售"
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💼 销售模式\n找潜在客户", use_container_width=True, key="mode_sales"):
            st.session_state.mode_selected = "销售"
            st.rerun()
    with col2:
        if st.button("🎓 求职模式\n找理想雇主", use_container_width=True, key="mode_job"):
            st.session_state.mode_selected = "求职"
            st.rerun()
    
    mode_key = st.session_state.mode_selected
    st.markdown(f'<div style="background:linear-gradient(135deg,#667eea,#764ba2);color:white;padding:10px 20px;border-radius:10px;text-align:center;font-weight:600;margin:8px 0 12px 0;">✅ 当前模式：{"💼 销售" if mode_key == "销售" else "🎓 求职"}</div>', unsafe_allow_html=True)
    
    # ===== AI 帮你写需求 =====
    with st.expander("🤖 AI 帮我写需求描述", expanded=False):
        st.caption("💡 填写信息后点击生成，AI 会自动生成需求描述，然后点击「填入输入框」")
        
        if mode_key == "销售":
            col_a, col_b = st.columns(2)
            with col_a:
                product = st.text_input("产品/服务", placeholder="AI客服系统", key="p1")
                target_industry = st.text_input("目标行业", placeholder="电商", key="p2")
            with col_b:
                target_size = st.text_input("目标规模", placeholder="500人以上", key="p3")
                pain_point = st.text_input("客户痛点", placeholder="客服响应慢", key="p4")
            extra = st.text_area("补充信息", placeholder="最近有融资的优先", key="p5", height=40)
        else:
            col_a, col_b = st.columns(2)
            with col_a:
                skill = st.text_input("核心技能", placeholder="前端开发", key="j1")
                tech_stack = st.text_input("技术栈", placeholder="React, TypeScript", key="j2")
            with col_b:
                target_industry_job = st.text_input("目标行业", placeholder="互联网", key="j3")
                job_level = st.text_input("目标职级", placeholder="中级", key="j4")
            extra = st.text_area("补充信息", placeholder="希望公司已盈利", key="j5", height=40)
        
        if st.button("🚀 生成需求描述", use_container_width=True, key="gen_btn"):
            if mode_key == "销售":
                info = f"产品：{product or '未填写'}\n行业：{target_industry or '未填写'}\n规模：{target_size or '未填写'}\n痛点：{pain_point or '未填写'}\n补充：{extra or '无'}"
                prompt_text = f"你是商业需求分析师。生成一段专业完整的需求描述（150-200字）。用户信息：\n{info}\n要求：直接输出描述，不要有其他内容。"
            else:
                info = f"技能：{skill or '未填写'}\n技术栈：{tech_stack or '未填写'}\n目标行业：{target_industry_job or '未填写'}\n职级：{job_level or '未填写'}\n补充：{extra or '无'}"
                prompt_text = f"你是职业规划师。生成一段专业完整的求职需求描述（150-200字）。用户信息：\n{info}\n要求：直接输出描述，不要有其他内容。"
            
            with st.spinner("🤖 AI 生成中..."):
                try:
                    resp = client.chat.completions.create(
                        model="deepseek-chat",
                        messages=[{"role": "system", "content": "你是专业文案助手。"}, {"role": "user", "content": prompt_text}],
                        temperature=0.7,
                        max_tokens=800
                    )
                    generated_text = resp.choices[0].message.content
                    st.session_state.generated_need = generated_text
                    
                    st.markdown("##### ✅ 生成结果：")
                    st.info(generated_text)
                    
                    if st.button("📥 填入输入框", use_container_width=True, key="fill_btn"):
                        # 直接修改 session_state 中 text_area 对应的 key
                        st.session_state.need_input = generated_text
                        st.success("✅ 已填入输入框！")
                        
                except Exception as e:
                    st.error(f"生成失败: {str(e)}")
    
    # ===== 需求输入框 =====
    # 初始化
    if 'need_input' not in st.session_state:
        st.session_state.need_input = ""
    
    # 用 key 直接绑定，不写 value
    st.text_area(
        "📝 描述你的需求",
        height=120,
        placeholder="示例：我销售AI客服系统，目标客户是电商和零售公司，有客服团队，最近有融资或扩张计划。",
        key="need_input"
    )
    
    if st.button("🔍 开始搜索", use_container_width=True, type="primary"):
        # 从 session_state 读取
        need_description = st.session_state.get("need_input", "")
        if not need_description:
            st.error("⚠️ 请先输入需求描述")
        else:
            result_df = quick_search(need_description, mode_key)
            if not result_df.empty:
                result_df = result_df.sort_values("综合评分", ascending=False)
                
                st.markdown("---")
                st.markdown(f"##### 📊 搜索结果 · 共 {len(result_df)} 家公司")
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("🏢 公司总数", len(result_df))
                with col2:
                    st.metric("🔥 高优先级", len(result_df[result_df['优先级'].str.contains('高')]))
                with col3:
                    st.metric("📊 平均评分", int(result_df['综合评分'].mean()))
                with col4:
                    st.metric("📡 数据源", len(result_df['数据来源'].unique()))
                
                st.markdown("---")
                
                for _, row in result_df.iterrows():
                    score = row['综合评分']
                    priority = row['优先级']
                    p_class = "priority-high" if "高" in str(priority) else "priority-mid" if "中" in str(priority) else "priority-low"
                    p_label = "🔥 高优先级" if "高" in str(priority) else "📌 中优先级" if "中" in str(priority) else "💤 低优先级"
                    
                    st.markdown(f"""
                    <div class="company-card">
                        <div style="display:flex;justify-content:space-between;align-items:center;">
                            <div><strong>{row['公司名称']}</strong> <span class="{p_class}">{p_label}</span></div>
                            <div><span style="font-size:24px;font-weight:700;color:#667eea;">{score}</span></div>
                        </div>
                        <div style="margin-top:6px;display:flex;flex-wrap:wrap;gap:4px;">
                            <span class="tag">🎯 匹配度: {row.get('匹配度', 'N/A')}</span>
                            <span class="tag">📡 {row.get('数据来源', '')}</span>
                            {f'<span class="tag">👤 {row["创始人"]}</span>' if row.get('创始人') else ''}
                            {f'<span class="tag">📅 {row["成立时间"]}</span>' if row.get('成立时间') else ''}
                            {f'<span class="tag">💼 {row["招聘数"]}个岗位</span>' if row.get('招聘数', 0) > 0 else ''}
                        </div>
                        <div style="margin-top:6px;font-size:14px;color:#3c4043;">{row.get('理由', '')[:100]}</div>
                        <div style="font-size:13px;color:#667eea;">💡 {row.get('建议动作', '')}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                csv = result_df.to_csv(index=False).encode('utf-8-sig')
                st.download_button("📥 下载结果 (CSV)", data=csv, file_name=f"觅镜_结果_{datetime.now().strftime('%Y%m%d')}.csv", mime="text/csv", use_container_width=True)# ============================================================
# TAB 1: 发现引擎（修复版）
# ============================================================
with tab_main:
    st.markdown("##### 选择使用场景")
    
    if 'mode_selected' not in st.session_state:
        st.session_state.mode_selected = "销售"
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💼 销售模式\n找潜在客户", use_container_width=True, key="mode_sales"):
            st.session_state.mode_selected = "销售"
            st.rerun()
    with col2:
        if st.button("🎓 求职模式\n找理想雇主", use_container_width=True, key="mode_job"):
            st.session_state.mode_selected = "求职"
            st.rerun()
    
    mode_key = st.session_state.mode_selected
    st.markdown(f'<div style="background:linear-gradient(135deg,#667eea,#764ba2);color:white;padding:10px 20px;border-radius:10px;text-align:center;font-weight:600;margin:8px 0 12px 0;">✅ 当前模式：{"💼 销售" if mode_key == "销售" else "🎓 求职"}</div>', unsafe_allow_html=True)
    
    # ===== AI 帮你写需求 =====
    with st.expander("🤖 AI 帮我写需求描述", expanded=False):
        st.caption("💡 填写信息后点击生成，AI 会自动生成需求描述，然后点击「填入输入框」")
        
        if mode_key == "销售":
            col_a, col_b = st.columns(2)
            with col_a:
                product = st.text_input("产品/服务", placeholder="AI客服系统", key="p1")
                target_industry = st.text_input("目标行业", placeholder="电商", key="p2")
            with col_b:
                target_size = st.text_input("目标规模", placeholder="500人以上", key="p3")
                pain_point = st.text_input("客户痛点", placeholder="客服响应慢", key="p4")
            extra = st.text_area("补充信息", placeholder="最近有融资的优先", key="p5", height=40)
        else:
            col_a, col_b = st.columns(2)
            with col_a:
                skill = st.text_input("核心技能", placeholder="前端开发", key="j1")
                tech_stack = st.text_input("技术栈", placeholder="React, TypeScript", key="j2")
            with col_b:
                target_industry_job = st.text_input("目标行业", placeholder="互联网", key="j3")
                job_level = st.text_input("目标职级", placeholder="中级", key="j4")
            extra = st.text_area("补充信息", placeholder="希望公司已盈利", key="j5", height=40)
        
        if st.button("🚀 生成需求描述", use_container_width=True, key="gen_btn"):
            if mode_key == "销售":
                info = f"产品：{product or '未填写'}\n行业：{target_industry or '未填写'}\n规模：{target_size or '未填写'}\n痛点：{pain_point or '未填写'}\n补充：{extra or '无'}"
                prompt_text = f"你是商业需求分析师。生成一段专业完整的需求描述（150-200字）。用户信息：\n{info}\n要求：直接输出描述，不要有其他内容。"
            else:
                info = f"技能：{skill or '未填写'}\n技术栈：{tech_stack or '未填写'}\n目标行业：{target_industry_job or '未填写'}\n职级：{job_level or '未填写'}\n补充：{extra or '无'}"
                prompt_text = f"你是职业规划师。生成一段专业完整的求职需求描述（150-200字）。用户信息：\n{info}\n要求：直接输出描述，不要有其他内容。"
            
            with st.spinner("🤖 AI 生成中..."):
                try:
                    resp = client.chat.completions.create(
                        model="deepseek-chat",
                        messages=[{"role": "system", "content": "你是专业文案助手。"}, {"role": "user", "content": prompt_text}],
                        temperature=0.7,
                        max_tokens=800
                    )
                    generated_text = resp.choices[0].message.content
                    st.session_state.generated_need = generated_text
                    
                    st.markdown("##### ✅ 生成结果：")
                    st.info(generated_text)
                    
                    if st.button("📥 填入输入框", use_container_width=True, key="fill_btn"):
                        # 直接修改 session_state 中 text_area 对应的 key
                        st.session_state.need_input = generated_text
                        st.success("✅ 已填入输入框！")
                        
                except Exception as e:
                    st.error(f"生成失败: {str(e)}")
    
    # ===== 需求输入框 =====
    # 初始化
    if 'need_input' not in st.session_state:
        st.session_state.need_input = ""
    
    # 用 key 直接绑定，不写 value
    st.text_area(
        "📝 描述你的需求",
        height=120,
        placeholder="示例：我销售AI客服系统，目标客户是电商和零售公司，有客服团队，最近有融资或扩张计划。",
        key="need_input"
    )
    
    if st.button("🔍 开始搜索", use_container_width=True, type="primary"):
        # 从 session_state 读取
        need_description = st.session_state.get("need_input", "")
        if not need_description:
            st.error("⚠️ 请先输入需求描述")
        else:
            result_df = quick_search(need_description, mode_key)
            if not result_df.empty:
                result_df = result_df.sort_values("综合评分", ascending=False)
                
                st.markdown("---")
                st.markdown(f"##### 📊 搜索结果 · 共 {len(result_df)} 家公司")
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("🏢 公司总数", len(result_df))
                with col2:
                    st.metric("🔥 高优先级", len(result_df[result_df['优先级'].str.contains('高')]))
                with col3:
                    st.metric("📊 平均评分", int(result_df['综合评分'].mean()))
                with col4:
                    st.metric("📡 数据源", len(result_df['数据来源'].unique()))
                
                st.markdown("---")
                
                for _, row in result_df.iterrows():
                    score = row['综合评分']
                    priority = row['优先级']
                    p_class = "priority-high" if "高" in str(priority) else "priority-mid" if "中" in str(priority) else "priority-low"
                    p_label = "🔥 高优先级" if "高" in str(priority) else "📌 中优先级" if "中" in str(priority) else "💤 低优先级"
                    
                    st.markdown(f"""
                    <div class="company-card">
                        <div style="display:flex;justify-content:space-between;align-items:center;">
                            <div><strong>{row['公司名称']}</strong> <span class="{p_class}">{p_label}</span></div>
                            <div><span style="font-size:24px;font-weight:700;color:#667eea;">{score}</span></div>
                        </div>
                        <div style="margin-top:6px;display:flex;flex-wrap:wrap;gap:4px;">
                            <span class="tag">🎯 匹配度: {row.get('匹配度', 'N/A')}</span>
                            <span class="tag">📡 {row.get('数据来源', '')}</span>
                            {f'<span class="tag">👤 {row["创始人"]}</span>' if row.get('创始人') else ''}
                            {f'<span class="tag">📅 {row["成立时间"]}</span>' if row.get('成立时间') else ''}
                            {f'<span class="tag">💼 {row["招聘数"]}个岗位</span>' if row.get('招聘数', 0) > 0 else ''}
                        </div>
                        <div style="margin-top:6px;font-size:14px;color:#3c4043;">{row.get('理由', '')[:100]}</div>
                        <div style="font-size:13px;color:#667eea;">💡 {row.get('建议动作', '')}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                csv = result_df.to_csv(index=False).encode('utf-8-sig')
                st.download_button("📥 下载结果 (CSV)", data=csv, file_name=f"觅镜_结果_{datetime.now().strftime('%Y%m%d')}.csv", mime="text/csv", use_container_width=True)# ============================================================
# TAB 1: 发现引擎（修复版）
# ============================================================
with tab_main:
    st.markdown("##### 选择使用场景")
    
    if 'mode_selected' not in st.session_state:
        st.session_state.mode_selected = "销售"
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💼 销售模式\n找潜在客户", use_container_width=True, key="mode_sales"):
            st.session_state.mode_selected = "销售"
            st.rerun()
    with col2:
        if st.button("🎓 求职模式\n找理想雇主", use_container_width=True, key="mode_job"):
            st.session_state.mode_selected = "求职"
            st.rerun()
    
    mode_key = st.session_state.mode_selected
    st.markdown(f'<div style="background:linear-gradient(135deg,#667eea,#764ba2);color:white;padding:10px 20px;border-radius:10px;text-align:center;font-weight:600;margin:8px 0 12px 0;">✅ 当前模式：{"💼 销售" if mode_key == "销售" else "🎓 求职"}</div>', unsafe_allow_html=True)
    
    # ===== AI 帮你写需求 =====
    with st.expander("🤖 AI 帮我写需求描述", expanded=False):
        st.caption("💡 填写信息后点击生成，AI 会自动生成需求描述，然后点击「填入输入框」")
        
        if mode_key == "销售":
            col_a, col_b = st.columns(2)
            with col_a:
                product = st.text_input("产品/服务", placeholder="AI客服系统", key="p1")
                target_industry = st.text_input("目标行业", placeholder="电商", key="p2")
            with col_b:
                target_size = st.text_input("目标规模", placeholder="500人以上", key="p3")
                pain_point = st.text_input("客户痛点", placeholder="客服响应慢", key="p4")
            extra = st.text_area("补充信息", placeholder="最近有融资的优先", key="p5", height=40)
        else:
            col_a, col_b = st.columns(2)
            with col_a:
                skill = st.text_input("核心技能", placeholder="前端开发", key="j1")
                tech_stack = st.text_input("技术栈", placeholder="React, TypeScript", key="j2")
            with col_b:
                target_industry_job = st.text_input("目标行业", placeholder="互联网", key="j3")
                job_level = st.text_input("目标职级", placeholder="中级", key="j4")
            extra = st.text_area("补充信息", placeholder="希望公司已盈利", key="j5", height=40)
        
        if st.button("🚀 生成需求描述", use_container_width=True, key="gen_btn"):
            if mode_key == "销售":
                info = f"产品：{product or '未填写'}\n行业：{target_industry or '未填写'}\n规模：{target_size or '未填写'}\n痛点：{pain_point or '未填写'}\n补充：{extra or '无'}"
                prompt_text = f"你是商业需求分析师。生成一段专业完整的需求描述（150-200字）。用户信息：\n{info}\n要求：直接输出描述，不要有其他内容。"
            else:
                info = f"技能：{skill or '未填写'}\n技术栈：{tech_stack or '未填写'}\n目标行业：{target_industry_job or '未填写'}\n职级：{job_level or '未填写'}\n补充：{extra or '无'}"
                prompt_text = f"你是职业规划师。生成一段专业完整的求职需求描述（150-200字）。用户信息：\n{info}\n要求：直接输出描述，不要有其他内容。"
            
            with st.spinner("🤖 AI 生成中..."):
                try:
                    resp = client.chat.completions.create(
                        model="deepseek-chat",
                        messages=[{"role": "system", "content": "你是专业文案助手。"}, {"role": "user", "content": prompt_text}],
                        temperature=0.7,
                        max_tokens=800
                    )
                    generated_text = resp.choices[0].message.content
                    st.session_state.generated_need = generated_text
                    
                    st.markdown("##### ✅ 生成结果：")
                    st.info(generated_text)
                    
                    if st.button("📥 填入输入框", use_container_width=True, key="fill_btn"):
                        # 直接修改 session_state 中 text_area 对应的 key
                        st.session_state.need_input = generated_text
                        st.success("✅ 已填入输入框！")
                        
                except Exception as e:
                    st.error(f"生成失败: {str(e)}")
    
    # ===== 需求输入框 =====
    # 初始化
    if 'need_input' not in st.session_state:
        st.session_state.need_input = ""
    
    # 用 key 直接绑定，不写 value
    st.text_area(
        "📝 描述你的需求",
        height=120,
        placeholder="示例：我销售AI客服系统，目标客户是电商和零售公司，有客服团队，最近有融资或扩张计划。",
        key="need_input"
    )
    
    if st.button("🔍 开始搜索", use_container_width=True, type="primary"):
        # 从 session_state 读取
        need_description = st.session_state.get("need_input", "")
        if not need_description:
            st.error("⚠️ 请先输入需求描述")
        else:
            result_df = quick_search(need_description, mode_key)
            if not result_df.empty:
                result_df = result_df.sort_values("综合评分", ascending=False)
                
                st.markdown("---")
                st.markdown(f"##### 📊 搜索结果 · 共 {len(result_df)} 家公司")
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("🏢 公司总数", len(result_df))
                with col2:
                    st.metric("🔥 高优先级", len(result_df[result_df['优先级'].str.contains('高')]))
                with col3:
                    st.metric("📊 平均评分", int(result_df['综合评分'].mean()))
                with col4:
                    st.metric("📡 数据源", len(result_df['数据来源'].unique()))
                
                st.markdown("---")
                
                for _, row in result_df.iterrows():
                    score = row['综合评分']
                    priority = row['优先级']
                    p_class = "priority-high" if "高" in str(priority) else "priority-mid" if "中" in str(priority) else "priority-low"
                    p_label = "🔥 高优先级" if "高" in str(priority) else "📌 中优先级" if "中" in str(priority) else "💤 低优先级"
                    
                    st.markdown(f"""
                    <div class="company-card">
                        <div style="display:flex;justify-content:space-between;align-items:center;">
                            <div><strong>{row['公司名称']}</strong> <span class="{p_class}">{p_label}</span></div>
                            <div><span style="font-size:24px;font-weight:700;color:#667eea;">{score}</span></div>
                        </div>
                        <div style="margin-top:6px;display:flex;flex-wrap:wrap;gap:4px;">
                            <span class="tag">🎯 匹配度: {row.get('匹配度', 'N/A')}</span>
                            <span class="tag">📡 {row.get('数据来源', '')}</span>
                            {f'<span class="tag">👤 {row["创始人"]}</span>' if row.get('创始人') else ''}
                            {f'<span class="tag">📅 {row["成立时间"]}</span>' if row.get('成立时间') else ''}
                            {f'<span class="tag">💼 {row["招聘数"]}个岗位</span>' if row.get('招聘数', 0) > 0 else ''}
                        </div>
                        <div style="margin-top:6px;font-size:14px;color:#3c4043;">{row.get('理由', '')[:100]}</div>
                        <div style="font-size:13px;color:#667eea;">💡 {row.get('建议动作', '')}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                csv = result_df.to_csv(index=False).encode('utf-8-sig')
                st.download_button("📥 下载结果 (CSV)", data=csv, file_name=f"觅镜_结果_{datetime.now().strftime('%Y%m%d')}.csv", mime="text/csv", use_container_width=True)# ============================================================
# TAB 1: 发现引擎（修复版）
# ============================================================
with tab_main:
    st.markdown("##### 选择使用场景")
    
    if 'mode_selected' not in st.session_state:
        st.session_state.mode_selected = "销售"
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💼 销售模式\n找潜在客户", use_container_width=True, key="mode_sales"):
            st.session_state.mode_selected = "销售"
            st.rerun()
    with col2:
        if st.button("🎓 求职模式\n找理想雇主", use_container_width=True, key="mode_job"):
            st.session_state.mode_selected = "求职"
            st.rerun()
    
    mode_key = st.session_state.mode_selected
    st.markdown(f'<div style="background:linear-gradient(135deg,#667eea,#764ba2);color:white;padding:10px 20px;border-radius:10px;text-align:center;font-weight:600;margin:8px 0 12px 0;">✅ 当前模式：{"💼 销售" if mode_key == "销售" else "🎓 求职"}</div>', unsafe_allow_html=True)
    
    # ===== AI 帮你写需求 =====
    with st.expander("🤖 AI 帮我写需求描述", expanded=False):
        st.caption("💡 填写信息后点击生成，AI 会自动生成需求描述，然后点击「填入输入框」")
        
        if mode_key == "销售":
            col_a, col_b = st.columns(2)
            with col_a:
                product = st.text_input("产品/服务", placeholder="AI客服系统", key="p1")
                target_industry = st.text_input("目标行业", placeholder="电商", key="p2")
            with col_b:
                target_size = st.text_input("目标规模", placeholder="500人以上", key="p3")
                pain_point = st.text_input("客户痛点", placeholder="客服响应慢", key="p4")
            extra = st.text_area("补充信息", placeholder="最近有融资的优先", key="p5", height=40)
        else:
            col_a, col_b = st.columns(2)
            with col_a:
                skill = st.text_input("核心技能", placeholder="前端开发", key="j1")
                tech_stack = st.text_input("技术栈", placeholder="React, TypeScript", key="j2")
            with col_b:
                target_industry_job = st.text_input("目标行业", placeholder="互联网", key="j3")
                job_level = st.text_input("目标职级", placeholder="中级", key="j4")
            extra = st.text_area("补充信息", placeholder="希望公司已盈利", key="j5", height=40)
        
        if st.button("🚀 生成需求描述", use_container_width=True, key="gen_btn"):
            if mode_key == "销售":
                info = f"产品：{product or '未填写'}\n行业：{target_industry or '未填写'}\n规模：{target_size or '未填写'}\n痛点：{pain_point or '未填写'}\n补充：{extra or '无'}"
                prompt_text = f"你是商业需求分析师。生成一段专业完整的需求描述（150-200字）。用户信息：\n{info}\n要求：直接输出描述，不要有其他内容。"
            else:
                info = f"技能：{skill or '未填写'}\n技术栈：{tech_stack or '未填写'}\n目标行业：{target_industry_job or '未填写'}\n职级：{job_level or '未填写'}\n补充：{extra or '无'}"
                prompt_text = f"你是职业规划师。生成一段专业完整的求职需求描述（150-200字）。用户信息：\n{info}\n要求：直接输出描述，不要有其他内容。"
            
            with st.spinner("🤖 AI 生成中..."):
                try:
                    resp = client.chat.completions.create(
                        model="deepseek-chat",
                        messages=[{"role": "system", "content": "你是专业文案助手。"}, {"role": "user", "content": prompt_text}],
                        temperature=0.7,
                        max_tokens=800
                    )
                    generated_text = resp.choices[0].message.content
                    st.session_state.generated_need = generated_text
                    
                    st.markdown("##### ✅ 生成结果：")
                    st.info(generated_text)
                    
                    if st.button("📥 填入输入框", use_container_width=True, key="fill_btn"):
                        # 直接修改 session_state 中 text_area 对应的 key
                        st.session_state.need_input = generated_text
                        st.success("✅ 已填入输入框！")
                        
                except Exception as e:
                    st.error(f"生成失败: {str(e)}")
    
    # ===== 需求输入框 =====
    # 初始化
    if 'need_input' not in st.session_state:
        st.session_state.need_input = ""
    
    # 用 key 直接绑定，不写 value
    st.text_area(
        "📝 描述你的需求",
        height=120,
        placeholder="示例：我销售AI客服系统，目标客户是电商和零售公司，有客服团队，最近有融资或扩张计划。",
        key="need_input"
    )
    
    if st.button("🔍 开始搜索", use_container_width=True, type="primary"):
        # 从 session_state 读取
        need_description = st.session_state.get("need_input", "")
        if not need_description:
            st.error("⚠️ 请先输入需求描述")
        else:
            result_df = quick_search(need_description, mode_key)
            if not result_df.empty:
                result_df = result_df.sort_values("综合评分", ascending=False)
                
                st.markdown("---")
                st.markdown(f"##### 📊 搜索结果 · 共 {len(result_df)} 家公司")
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("🏢 公司总数", len(result_df))
                with col2:
                    st.metric("🔥 高优先级", len(result_df[result_df['优先级'].str.contains('高')]))
                with col3:
                    st.metric("📊 平均评分", int(result_df['综合评分'].mean()))
                with col4:
                    st.metric("📡 数据源", len(result_df['数据来源'].unique()))
                
                st.markdown("---")
                
                for _, row in result_df.iterrows():
                    score = row['综合评分']
                    priority = row['优先级']
                    p_class = "priority-high" if "高" in str(priority) else "priority-mid" if "中" in str(priority) else "priority-low"
                    p_label = "🔥 高优先级" if "高" in str(priority) else "📌 中优先级" if "中" in str(priority) else "💤 低优先级"
                    
                    st.markdown(f"""
                    <div class="company-card">
                        <div style="display:flex;justify-content:space-between;align-items:center;">
                            <div><strong>{row['公司名称']}</strong> <span class="{p_class}">{p_label}</span></div>
                            <div><span style="font-size:24px;font-weight:700;color:#667eea;">{score}</span></div>
                        </div>
                        <div style="margin-top:6px;display:flex;flex-wrap:wrap;gap:4px;">
                            <span class="tag">🎯 匹配度: {row.get('匹配度', 'N/A')}</span>
                            <span class="tag">📡 {row.get('数据来源', '')}</span>
                            {f'<span class="tag">👤 {row["创始人"]}</span>' if row.get('创始人') else ''}
                            {f'<span class="tag">📅 {row["成立时间"]}</span>' if row.get('成立时间') else ''}
                            {f'<span class="tag">💼 {row["招聘数"]}个岗位</span>' if row.get('招聘数', 0) > 0 else ''}
                        </div>
                        <div style="margin-top:6px;font-size:14px;color:#3c4043;">{row.get('理由', '')[:100]}</div>
                        <div style="font-size:13px;color:#667eea;">💡 {row.get('建议动作', '')}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                csv = result_df.to_csv(index=False).encode('utf-8-sig')
                st.download_button("📥 下载结果 (CSV)", data=csv, file_name=f"觅镜_结果_{datetime.now().strftime('%Y%m%d')}.csv", mime="text/csv", use_container_width=True)# ============================================================
# TAB 1: 发现引擎（修复版）
# ============================================================
with tab_main:
    st.markdown("##### 选择使用场景")
    
    if 'mode_selected' not in st.session_state:
        st.session_state.mode_selected = "销售"
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💼 销售模式\n找潜在客户", use_container_width=True, key="mode_sales"):
            st.session_state.mode_selected = "销售"
            st.rerun()
    with col2:
        if st.button("🎓 求职模式\n找理想雇主", use_container_width=True, key="mode_job"):
            st.session_state.mode_selected = "求职"
            st.rerun()
    
    mode_key = st.session_state.mode_selected
    st.markdown(f'<div style="background:linear-gradient(135deg,#667eea,#764ba2);color:white;padding:10px 20px;border-radius:10px;text-align:center;font-weight:600;margin:8px 0 12px 0;">✅ 当前模式：{"💼 销售" if mode_key == "销售" else "🎓 求职"}</div>', unsafe_allow_html=True)
    
    # ===== AI 帮你写需求 =====
    with st.expander("🤖 AI 帮我写需求描述", expanded=False):
        st.caption("💡 填写信息后点击生成，AI 会自动生成需求描述，然后点击「填入输入框」")
        
        if mode_key == "销售":
            col_a, col_b = st.columns(2)
            with col_a:
                product = st.text_input("产品/服务", placeholder="AI客服系统", key="p1")
                target_industry = st.text_input("目标行业", placeholder="电商", key="p2")
            with col_b:
                target_size = st.text_input("目标规模", placeholder="500人以上", key="p3")
                pain_point = st.text_input("客户痛点", placeholder="客服响应慢", key="p4")
            extra = st.text_area("补充信息", placeholder="最近有融资的优先", key="p5", height=40)
        else:
            col_a, col_b = st.columns(2)
            with col_a:
                skill = st.text_input("核心技能", placeholder="前端开发", key="j1")
                tech_stack = st.text_input("技术栈", placeholder="React, TypeScript", key="j2")
            with col_b:
                target_industry_job = st.text_input("目标行业", placeholder="互联网", key="j3")
                job_level = st.text_input("目标职级", placeholder="中级", key="j4")
            extra = st.text_area("补充信息", placeholder="希望公司已盈利", key="j5", height=40)
        
        if st.button("🚀 生成需求描述", use_container_width=True, key="gen_btn"):
            if mode_key == "销售":
                info = f"产品：{product or '未填写'}\n行业：{target_industry or '未填写'}\n规模：{target_size or '未填写'}\n痛点：{pain_point or '未填写'}\n补充：{extra or '无'}"
                prompt_text = f"你是商业需求分析师。生成一段专业完整的需求描述（150-200字）。用户信息：\n{info}\n要求：直接输出描述，不要有其他内容。"
            else:
                info = f"技能：{skill or '未填写'}\n技术栈：{tech_stack or '未填写'}\n目标行业：{target_industry_job or '未填写'}\n职级：{job_level or '未填写'}\n补充：{extra or '无'}"
                prompt_text = f"你是职业规划师。生成一段专业完整的求职需求描述（150-200字）。用户信息：\n{info}\n要求：直接输出描述，不要有其他内容。"
            
            with st.spinner("🤖 AI 生成中..."):
                try:
                    resp = client.chat.completions.create(
                        model="deepseek-chat",
                        messages=[{"role": "system", "content": "你是专业文案助手。"}, {"role": "user", "content": prompt_text}],
                        temperature=0.7,
                        max_tokens=800
                    )
                    generated_text = resp.choices[0].message.content
                    st.session_state.generated_need = generated_text
                    
                    st.markdown("##### ✅ 生成结果：")
                    st.info(generated_text)
                    
                    if st.button("📥 填入输入框", use_container_width=True, key="fill_btn"):
                        # 直接修改 session_state 中 text_area 对应的 key
                        st.session_state.need_input = generated_text
                        st.success("✅ 已填入输入框！")
                        
                except Exception as e:
                    st.error(f"生成失败: {str(e)}")
    
    # ===== 需求输入框 =====
    # 初始化
    if 'need_input' not in st.session_state:
        st.session_state.need_input = ""
    
    # 用 key 直接绑定，不写 value
    st.text_area(
        "📝 描述你的需求",
        height=120,
        placeholder="示例：我销售AI客服系统，目标客户是电商和零售公司，有客服团队，最近有融资或扩张计划。",
        key="need_input"
    )
    
    if st.button("🔍 开始搜索", use_container_width=True, type="primary"):
        # 从 session_state 读取
        need_description = st.session_state.get("need_input", "")
        if not need_description:
            st.error("⚠️ 请先输入需求描述")
        else:
            result_df = quick_search(need_description, mode_key)
            if not result_df.empty:
                result_df = result_df.sort_values("综合评分", ascending=False)
                
                st.markdown("---")
                st.markdown(f"##### 📊 搜索结果 · 共 {len(result_df)} 家公司")
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("🏢 公司总数", len(result_df))
                with col2:
                    st.metric("🔥 高优先级", len(result_df[result_df['优先级'].str.contains('高')]))
                with col3:
                    st.metric("📊 平均评分", int(result_df['综合评分'].mean()))
                with col4:
                    st.metric("📡 数据源", len(result_df['数据来源'].unique()))
                
                st.markdown("---")
                
                for _, row in result_df.iterrows():
                    score = row['综合评分']
                    priority = row['优先级']
                    p_class = "priority-high" if "高" in str(priority) else "priority-mid" if "中" in str(priority) else "priority-low"
                    p_label = "🔥 高优先级" if "高" in str(priority) else "📌 中优先级" if "中" in str(priority) else "💤 低优先级"
                    
                    st.markdown(f"""
                    <div class="company-card">
                        <div style="display:flex;justify-content:space-between;align-items:center;">
                            <div><strong>{row['公司名称']}</strong> <span class="{p_class}">{p_label}</span></div>
                            <div><span style="font-size:24px;font-weight:700;color:#667eea;">{score}</span></div>
                        </div>
                        <div style="margin-top:6px;display:flex;flex-wrap:wrap;gap:4px;">
                            <span class="tag">🎯 匹配度: {row.get('匹配度', 'N/A')}</span>
                            <span class="tag">📡 {row.get('数据来源', '')}</span>
                            {f'<span class="tag">👤 {row["创始人"]}</span>' if row.get('创始人') else ''}
                            {f'<span class="tag">📅 {row["成立时间"]}</span>' if row.get('成立时间') else ''}
                            {f'<span class="tag">💼 {row["招聘数"]}个岗位</span>' if row.get('招聘数', 0) > 0 else ''}
                        </div>
                        <div style="margin-top:6px;font-size:14px;color:#3c4043;">{row.get('理由', '')[:100]}</div>
                        <div style="font-size:13px;color:#667eea;">💡 {row.get('建议动作', '')}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                csv = result_df.to_csv(index=False).encode('utf-8-sig')
                st.download_button("📥 下载结果 (CSV)", data=csv, file_name=f"觅镜_结果_{datetime.now().strftime('%Y%m%d')}.csv", mime="text/csv", use_container_width=True)# ============================================================
# TAB 1: 发现引擎（修复版）
# ============================================================
with tab_main:
    st.markdown("##### 选择使用场景")
    
    if 'mode_selected' not in st.session_state:
        st.session_state.mode_selected = "销售"
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💼 销售模式\n找潜在客户", use_container_width=True, key="mode_sales"):
            st.session_state.mode_selected = "销售"
            st.rerun()
    with col2:
        if st.button("🎓 求职模式\n找理想雇主", use_container_width=True, key="mode_job"):
            st.session_state.mode_selected = "求职"
            st.rerun()
    
    mode_key = st.session_state.mode_selected
    st.markdown(f'<div style="background:linear-gradient(135deg,#667eea,#764ba2);color:white;padding:10px 20px;border-radius:10px;text-align:center;font-weight:600;margin:8px 0 12px 0;">✅ 当前模式：{"💼 销售" if mode_key == "销售" else "🎓 求职"}</div>', unsafe_allow_html=True)
    
    # ===== AI 帮你写需求 =====
    with st.expander("🤖 AI 帮我写需求描述", expanded=False):
        st.caption("💡 填写信息后点击生成，AI 会自动生成需求描述，然后点击「填入输入框」")
        
        if mode_key == "销售":
            col_a, col_b = st.columns(2)
            with col_a:
                product = st.text_input("产品/服务", placeholder="AI客服系统", key="p1")
                target_industry = st.text_input("目标行业", placeholder="电商", key="p2")
            with col_b:
                target_size = st.text_input("目标规模", placeholder="500人以上", key="p3")
                pain_point = st.text_input("客户痛点", placeholder="客服响应慢", key="p4")
            extra = st.text_area("补充信息", placeholder="最近有融资的优先", key="p5", height=40)
        else:
            col_a, col_b = st.columns(2)
            with col_a:
                skill = st.text_input("核心技能", placeholder="前端开发", key="j1")
                tech_stack = st.text_input("技术栈", placeholder="React, TypeScript", key="j2")
            with col_b:
                target_industry_job = st.text_input("目标行业", placeholder="互联网", key="j3")
                job_level = st.text_input("目标职级", placeholder="中级", key="j4")
            extra = st.text_area("补充信息", placeholder="希望公司已盈利", key="j5", height=40)
        
        if st.button("🚀 生成需求描述", use_container_width=True, key="gen_btn"):
            if mode_key == "销售":
                info = f"产品：{product or '未填写'}\n行业：{target_industry or '未填写'}\n规模：{target_size or '未填写'}\n痛点：{pain_point or '未填写'}\n补充：{extra or '无'}"
                prompt_text = f"你是商业需求分析师。生成一段专业完整的需求描述（150-200字）。用户信息：\n{info}\n要求：直接输出描述，不要有其他内容。"
            else:
                info = f"技能：{skill or '未填写'}\n技术栈：{tech_stack or '未填写'}\n目标行业：{target_industry_job or '未填写'}\n职级：{job_level or '未填写'}\n补充：{extra or '无'}"
                prompt_text = f"你是职业规划师。生成一段专业完整的求职需求描述（150-200字）。用户信息：\n{info}\n要求：直接输出描述，不要有其他内容。"
            
            with st.spinner("🤖 AI 生成中..."):
                try:
                    resp = client.chat.completions.create(
                        model="deepseek-chat",
                        messages=[{"role": "system", "content": "你是专业文案助手。"}, {"role": "user", "content": prompt_text}],
                        temperature=0.7,
                        max_tokens=800
                    )
                    generated_text = resp.choices[0].message.content
                    st.session_state.generated_need = generated_text
                    
                    st.markdown("##### ✅ 生成结果：")
                    st.info(generated_text)
                    
                    if st.button("📥 填入输入框", use_container_width=True, key="fill_btn"):
                        # 直接修改 session_state 中 text_area 对应的 key
                        st.session_state.need_input = generated_text
                        st.success("✅ 已填入输入框！")
                        
                except Exception as e:
                    st.error(f"生成失败: {str(e)}")
    
    # ===== 需求输入框 =====
    # 初始化
    if 'need_input' not in st.session_state:
        st.session_state.need_input = ""
    
    # 用 key 直接绑定，不写 value
    st.text_area(
        "📝 描述你的需求",
        height=120,
        placeholder="示例：我销售AI客服系统，目标客户是电商和零售公司，有客服团队，最近有融资或扩张计划。",
        key="need_input"
    )
    
    if st.button("🔍 开始搜索", use_container_width=True, type="primary"):
        # 从 session_state 读取
        need_description = st.session_state.get("need_input", "")
        if not need_description:
            st.error("⚠️ 请先输入需求描述")
        else:
            result_df = quick_search(need_description, mode_key)
            if not result_df.empty:
                result_df = result_df.sort_values("综合评分", ascending=False)
                
                st.markdown("---")
                st.markdown(f"##### 📊 搜索结果 · 共 {len(result_df)} 家公司")
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("🏢 公司总数", len(result_df))
                with col2:
                    st.metric("🔥 高优先级", len(result_df[result_df['优先级'].str.contains('高')]))
                with col3:
                    st.metric("📊 平均评分", int(result_df['综合评分'].mean()))
                with col4:
                    st.metric("📡 数据源", len(result_df['数据来源'].unique()))
                
                st.markdown("---")
                
                for _, row in result_df.iterrows():
                    score = row['综合评分']
                    priority = row['优先级']
                    p_class = "priority-high" if "高" in str(priority) else "priority-mid" if "中" in str(priority) else "priority-low"
                    p_label = "🔥 高优先级" if "高" in str(priority) else "📌 中优先级" if "中" in str(priority) else "💤 低优先级"
                    
                    st.markdown(f"""
                    <div class="company-card">
                        <div style="display:flex;justify-content:space-between;align-items:center;">
                            <div><strong>{row['公司名称']}</strong> <span class="{p_class}">{p_label}</span></div>
                            <div><span style="font-size:24px;font-weight:700;color:#667eea;">{score}</span></div>
                        </div>
                        <div style="margin-top:6px;display:flex;flex-wrap:wrap;gap:4px;">
                            <span class="tag">🎯 匹配度: {row.get('匹配度', 'N/A')}</span>
                            <span class="tag">📡 {row.get('数据来源', '')}</span>
                            {f'<span class="tag">👤 {row["创始人"]}</span>' if row.get('创始人') else ''}
                            {f'<span class="tag">📅 {row["成立时间"]}</span>' if row.get('成立时间') else ''}
                            {f'<span class="tag">💼 {row["招聘数"]}个岗位</span>' if row.get('招聘数', 0) > 0 else ''}
                        </div>
                        <div style="margin-top:6px;font-size:14px;color:#3c4043;">{row.get('理由', '')[:100]}</div>
                        <div style="font-size:13px;color:#667eea;">💡 {row.get('建议动作', '')}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                csv = result_df.to_csv(index=False).encode('utf-8-sig')
                st.download_button("📥 下载结果 (CSV)", data=csv, file_name=f"觅镜_结果_{datetime.now().strftime('%Y%m%d')}.csv", mime="text/csv", use_container_width=True)# ============================================================
# TAB 1: 发现引擎（修复版）
# ============================================================
with tab_main:
    st.markdown("##### 选择使用场景")
    
    if 'mode_selected' not in st.session_state:
        st.session_state.mode_selected = "销售"
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💼 销售模式\n找潜在客户", use_container_width=True, key="mode_sales"):
            st.session_state.mode_selected = "销售"
            st.rerun()
    with col2:
        if st.button("🎓 求职模式\n找理想雇主", use_container_width=True, key="mode_job"):
            st.session_state.mode_selected = "求职"
            st.rerun()
    
    mode_key = st.session_state.mode_selected
    st.markdown(f'<div style="background:linear-gradient(135deg,#667eea,#764ba2);color:white;padding:10px 20px;border-radius:10px;text-align:center;font-weight:600;margin:8px 0 12px 0;">✅ 当前模式：{"💼 销售" if mode_key == "销售" else "🎓 求职"}</div>', unsafe_allow_html=True)
    
    # ===== AI 帮你写需求 =====
    with st.expander("🤖 AI 帮我写需求描述", expanded=False):
        st.caption("💡 填写信息后点击生成，AI 会自动生成需求描述，然后点击「填入输入框」")
        
        if mode_key == "销售":
            col_a, col_b = st.columns(2)
            with col_a:
                product = st.text_input("产品/服务", placeholder="AI客服系统", key="p1")
                target_industry = st.text_input("目标行业", placeholder="电商", key="p2")
            with col_b:
                target_size = st.text_input("目标规模", placeholder="500人以上", key="p3")
                pain_point = st.text_input("客户痛点", placeholder="客服响应慢", key="p4")
            extra = st.text_area("补充信息", placeholder="最近有融资的优先", key="p5", height=40)
        else:
            col_a, col_b = st.columns(2)
            with col_a:
                skill = st.text_input("核心技能", placeholder="前端开发", key="j1")
                tech_stack = st.text_input("技术栈", placeholder="React, TypeScript", key="j2")
            with col_b:
                target_industry_job = st.text_input("目标行业", placeholder="互联网", key="j3")
                job_level = st.text_input("目标职级", placeholder="中级", key="j4")
            extra = st.text_area("补充信息", placeholder="希望公司已盈利", key="j5", height=40)
        
        if st.button("🚀 生成需求描述", use_container_width=True, key="gen_btn"):
            if mode_key == "销售":
                info = f"产品：{product or '未填写'}\n行业：{target_industry or '未填写'}\n规模：{target_size or '未填写'}\n痛点：{pain_point or '未填写'}\n补充：{extra or '无'}"
                prompt_text = f"你是商业需求分析师。生成一段专业完整的需求描述（150-200字）。用户信息：\n{info}\n要求：直接输出描述，不要有其他内容。"
            else:
                info = f"技能：{skill or '未填写'}\n技术栈：{tech_stack or '未填写'}\n目标行业：{target_industry_job or '未填写'}\n职级：{job_level or '未填写'}\n补充：{extra or '无'}"
                prompt_text = f"你是职业规划师。生成一段专业完整的求职需求描述（150-200字）。用户信息：\n{info}\n要求：直接输出描述，不要有其他内容。"
            
            with st.spinner("🤖 AI 生成中..."):
                try:
                    resp = client.chat.completions.create(
                        model="deepseek-chat",
                        messages=[{"role": "system", "content": "你是专业文案助手。"}, {"role": "user", "content": prompt_text}],
                        temperature=0.7,
                        max_tokens=800
                    )
                    generated_text = resp.choices[0].message.content
                    st.session_state.generated_need = generated_text
                    
                    st.markdown("##### ✅ 生成结果：")
                    st.info(generated_text)
                    
                    if st.button("📥 填入输入框", use_container_width=True, key="fill_btn"):
                        # 直接修改 session_state 中 text_area 对应的 key
                        st.session_state.need_input = generated_text
                        st.success("✅ 已填入输入框！")
                        
                except Exception as e:
                    st.error(f"生成失败: {str(e)}")
    
    # ===== 需求输入框 =====
    # 初始化
    if 'need_input' not in st.session_state:
        st.session_state.need_input = ""
    
    # 用 key 直接绑定，不写 value
    st.text_area(
        "📝 描述你的需求",
        height=120,
        placeholder="示例：我销售AI客服系统，目标客户是电商和零售公司，有客服团队，最近有融资或扩张计划。",
        key="need_input"
    )
    
    if st.button("🔍 开始搜索", use_container_width=True, type="primary"):
        # 从 session_state 读取
        need_description = st.session_state.get("need_input", "")
        if not need_description:
            st.error("⚠️ 请先输入需求描述")
        else:
            result_df = quick_search(need_description, mode_key)
            if not result_df.empty:
                result_df = result_df.sort_values("综合评分", ascending=False)
                
                st.markdown("---")
                st.markdown(f"##### 📊 搜索结果 · 共 {len(result_df)} 家公司")
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("🏢 公司总数", len(result_df))
                with col2:
                    st.metric("🔥 高优先级", len(result_df[result_df['优先级'].str.contains('高')]))
                with col3:
                    st.metric("📊 平均评分", int(result_df['综合评分'].mean()))
                with col4:
                    st.metric("📡 数据源", len(result_df['数据来源'].unique()))
                
                st.markdown("---")
                
                for _, row in result_df.iterrows():
                    score = row['综合评分']
                    priority = row['优先级']
                    p_class = "priority-high" if "高" in str(priority) else "priority-mid" if "中" in str(priority) else "priority-low"
                    p_label = "🔥 高优先级" if "高" in str(priority) else "📌 中优先级" if "中" in str(priority) else "💤 低优先级"
                    
                    st.markdown(f"""
                    <div class="company-card">
                        <div style="display:flex;justify-content:space-between;align-items:center;">
                            <div><strong>{row['公司名称']}</strong> <span class="{p_class}">{p_label}</span></div>
                            <div><span style="font-size:24px;font-weight:700;color:#667eea;">{score}</span></div>
                        </div>
                        <div style="margin-top:6px;display:flex;flex-wrap:wrap;gap:4px;">
                            <span class="tag">🎯 匹配度: {row.get('匹配度', 'N/A')}</span>
                            <span class="tag">📡 {row.get('数据来源', '')}</span>
                            {f'<span class="tag">👤 {row["创始人"]}</span>' if row.get('创始人') else ''}
                            {f'<span class="tag">📅 {row["成立时间"]}</span>' if row.get('成立时间') else ''}
                            {f'<span class="tag">💼 {row["招聘数"]}个岗位</span>' if row.get('招聘数', 0) > 0 else ''}
                        </div>
                        <div style="margin-top:6px;font-size:14px;color:#3c4043;">{row.get('理由', '')[:100]}</div>
                        <div style="font-size:13px;color:#667eea;">💡 {row.get('建议动作', '')}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                csv = result_df.to_csv(index=False).encode('utf-8-sig')
                st.download_button("📥 下载结果 (CSV)", data=csv, file_name=f"觅镜_结果_{datetime.now().strftime('%Y%m%d')}.csv", mime="text/csv", use_container_width=True)# ============================================================
# TAB 1: 发现引擎（修复版）
# ============================================================
with tab_main:
    st.markdown("##### 选择使用场景")
    
    if 'mode_selected' not in st.session_state:
        st.session_state.mode_selected = "销售"
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💼 销售模式\n找潜在客户", use_container_width=True, key="mode_sales"):
            st.session_state.mode_selected = "销售"
            st.rerun()
    with col2:
        if st.button("🎓 求职模式\n找理想雇主", use_container_width=True, key="mode_job"):
            st.session_state.mode_selected = "求职"
            st.rerun()
    
    mode_key = st.session_state.mode_selected
    st.markdown(f'<div style="background:linear-gradient(135deg,#667eea,#764ba2);color:white;padding:10px 20px;border-radius:10px;text-align:center;font-weight:600;margin:8px 0 12px 0;">✅ 当前模式：{"💼 销售" if mode_key == "销售" else "🎓 求职"}</div>', unsafe_allow_html=True)
    
    # ===== AI 帮你写需求 =====
    with st.expander("🤖 AI 帮我写需求描述", expanded=False):
        st.caption("💡 填写信息后点击生成，AI 会自动生成需求描述，然后点击「填入输入框」")
        
        if mode_key == "销售":
            col_a, col_b = st.columns(2)
            with col_a:
                product = st.text_input("产品/服务", placeholder="AI客服系统", key="p1")
                target_industry = st.text_input("目标行业", placeholder="电商", key="p2")
            with col_b:
                target_size = st.text_input("目标规模", placeholder="500人以上", key="p3")
                pain_point = st.text_input("客户痛点", placeholder="客服响应慢", key="p4")
            extra = st.text_area("补充信息", placeholder="最近有融资的优先", key="p5", height=40)
        else:
            col_a, col_b = st.columns(2)
            with col_a:
                skill = st.text_input("核心技能", placeholder="前端开发", key="j1")
                tech_stack = st.text_input("技术栈", placeholder="React, TypeScript", key="j2")
            with col_b:
                target_industry_job = st.text_input("目标行业", placeholder="互联网", key="j3")
                job_level = st.text_input("目标职级", placeholder="中级", key="j4")
            extra = st.text_area("补充信息", placeholder="希望公司已盈利", key="j5", height=40)
        
        if st.button("🚀 生成需求描述", use_container_width=True, key="gen_btn"):
            if mode_key == "销售":
                info = f"产品：{product or '未填写'}\n行业：{target_industry or '未填写'}\n规模：{target_size or '未填写'}\n痛点：{pain_point or '未填写'}\n补充：{extra or '无'}"
                prompt_text = f"你是商业需求分析师。生成一段专业完整的需求描述（150-200字）。用户信息：\n{info}\n要求：直接输出描述，不要有其他内容。"
            else:
                info = f"技能：{skill or '未填写'}\n技术栈：{tech_stack or '未填写'}\n目标行业：{target_industry_job or '未填写'}\n职级：{job_level or '未填写'}\n补充：{extra or '无'}"
                prompt_text = f"你是职业规划师。生成一段专业完整的求职需求描述（150-200字）。用户信息：\n{info}\n要求：直接输出描述，不要有其他内容。"
            
            with st.spinner("🤖 AI 生成中..."):
                try:
                    resp = client.chat.completions.create(
                        model="deepseek-chat",
                        messages=[{"role": "system", "content": "你是专业文案助手。"}, {"role": "user", "content": prompt_text}],
                        temperature=0.7,
                        max_tokens=800
                    )
                    generated_text = resp.choices[0].message.content
                    st.session_state.generated_need = generated_text
                    
                    st.markdown("##### ✅ 生成结果：")
                    st.info(generated_text)
                    
                    if st.button("📥 填入输入框", use_container_width=True, key="fill_btn"):
                        # 直接修改 session_state 中 text_area 对应的 key
                        st.session_state.need_input = generated_text
                        st.success("✅ 已填入输入框！")
                        
                except Exception as e:
                    st.error(f"生成失败: {str(e)}")
    
    # ===== 需求输入框 =====
    # 初始化
    if 'need_input' not in st.session_state:
        st.session_state.need_input = ""
    
    # 用 key 直接绑定，不写 value
    st.text_area(
        "📝 描述你的需求",
        height=120,
        placeholder="示例：我销售AI客服系统，目标客户是电商和零售公司，有客服团队，最近有融资或扩张计划。",
        key="need_input"
    )
    
    if st.button("🔍 开始搜索", use_container_width=True, type="primary"):
        # 从 session_state 读取
        need_description = st.session_state.get("need_input", "")
        if not need_description:
            st.error("⚠️ 请先输入需求描述")
        else:
            result_df = quick_search(need_description, mode_key)
            if not result_df.empty:
                result_df = result_df.sort_values("综合评分", ascending=False)
                
                st.markdown("---")
                st.markdown(f"##### 📊 搜索结果 · 共 {len(result_df)} 家公司")
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("🏢 公司总数", len(result_df))
                with col2:
                    st.metric("🔥 高优先级", len(result_df[result_df['优先级'].str.contains('高')]))
                with col3:
                    st.metric("📊 平均评分", int(result_df['综合评分'].mean()))
                with col4:
                    st.metric("📡 数据源", len(result_df['数据来源'].unique()))
                
                st.markdown("---")
                
                for _, row in result_df.iterrows():
                    score = row['综合评分']
                    priority = row['优先级']
                    p_class = "priority-high" if "高" in str(priority) else "priority-mid" if "中" in str(priority) else "priority-low"
                    p_label = "🔥 高优先级" if "高" in str(priority) else "📌 中优先级" if "中" in str(priority) else "💤 低优先级"
                    
                    st.markdown(f"""
                    <div class="company-card">
                        <div style="display:flex;justify-content:space-between;align-items:center;">
                            <div><strong>{row['公司名称']}</strong> <span class="{p_class}">{p_label}</span></div>
                            <div><span style="font-size:24px;font-weight:700;color:#667eea;">{score}</span></div>
                        </div>
                        <div style="margin-top:6px;display:flex;flex-wrap:wrap;gap:4px;">
                            <span class="tag">🎯 匹配度: {row.get('匹配度', 'N/A')}</span>
                            <span class="tag">📡 {row.get('数据来源', '')}</span>
                            {f'<span class="tag">👤 {row["创始人"]}</span>' if row.get('创始人') else ''}
                            {f'<span class="tag">📅 {row["成立时间"]}</span>' if row.get('成立时间') else ''}
                            {f'<span class="tag">💼 {row["招聘数"]}个岗位</span>' if row.get('招聘数', 0) > 0 else ''}
                        </div>
                        <div style="margin-top:6px;font-size:14px;color:#3c4043;">{row.get('理由', '')[:100]}</div>
                        <div style="font-size:13px;color:#667eea;">💡 {row.get('建议动作', '')}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                csv = result_df.to_csv(index=False).encode('utf-8-sig')
                st.download_button("📥 下载结果 (CSV)", data=csv, file_name=f"觅镜_结果_{datetime.now().strftime('%Y%m%d')}.csv", mime="text/csv", use_container_width=True)# ============================================================
# TAB 1: 发现引擎（修复版）
# ============================================================
with tab_main:
    st.markdown("##### 选择使用场景")
    
    if 'mode_selected' not in st.session_state:
        st.session_state.mode_selected = "销售"
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💼 销售模式\n找潜在客户", use_container_width=True, key="mode_sales"):
            st.session_state.mode_selected = "销售"
            st.rerun()
    with col2:
        if st.button("🎓 求职模式\n找理想雇主", use_container_width=True, key="mode_job"):
            st.session_state.mode_selected = "求职"
            st.rerun()
    
    mode_key = st.session_state.mode_selected
    st.markdown(f'<div style="background:linear-gradient(135deg,#667eea,#764ba2);color:white;padding:10px 20px;border-radius:10px;text-align:center;font-weight:600;margin:8px 0 12px 0;">✅ 当前模式：{"💼 销售" if mode_key == "销售" else "🎓 求职"}</div>', unsafe_allow_html=True)
    
    # ===== AI 帮你写需求 =====
    with st.expander("🤖 AI 帮我写需求描述", expanded=False):
        st.caption("💡 填写信息后点击生成，AI 会自动生成需求描述，然后点击「填入输入框」")
        
        if mode_key == "销售":
            col_a, col_b = st.columns(2)
            with col_a:
                product = st.text_input("产品/服务", placeholder="AI客服系统", key="p1")
                target_industry = st.text_input("目标行业", placeholder="电商", key="p2")
            with col_b:
                target_size = st.text_input("目标规模", placeholder="500人以上", key="p3")
                pain_point = st.text_input("客户痛点", placeholder="客服响应慢", key="p4")
            extra = st.text_area("补充信息", placeholder="最近有融资的优先", key="p5", height=40)
        else:
            col_a, col_b = st.columns(2)
            with col_a:
                skill = st.text_input("核心技能", placeholder="前端开发", key="j1")
                tech_stack = st.text_input("技术栈", placeholder="React, TypeScript", key="j2")
            with col_b:
                target_industry_job = st.text_input("目标行业", placeholder="互联网", key="j3")
                job_level = st.text_input("目标职级", placeholder="中级", key="j4")
            extra = st.text_area("补充信息", placeholder="希望公司已盈利", key="j5", height=40)
        
        if st.button("🚀 生成需求描述", use_container_width=True, key="gen_btn"):
            if mode_key == "销售":
                info = f"产品：{product or '未填写'}\n行业：{target_industry or '未填写'}\n规模：{target_size or '未填写'}\n痛点：{pain_point or '未填写'}\n补充：{extra or '无'}"
                prompt_text = f"你是商业需求分析师。生成一段专业完整的需求描述（150-200字）。用户信息：\n{info}\n要求：直接输出描述，不要有其他内容。"
            else:
                info = f"技能：{skill or '未填写'}\n技术栈：{tech_stack or '未填写'}\n目标行业：{target_industry_job or '未填写'}\n职级：{job_level or '未填写'}\n补充：{extra or '无'}"
                prompt_text = f"你是职业规划师。生成一段专业完整的求职需求描述（150-200字）。用户信息：\n{info}\n要求：直接输出描述，不要有其他内容。"
            
            with st.spinner("🤖 AI 生成中..."):
                try:
                    resp = client.chat.completions.create(
                        model="deepseek-chat",
                        messages=[{"role": "system", "content": "你是专业文案助手。"}, {"role": "user", "content": prompt_text}],
                        temperature=0.7,
                        max_tokens=800
                    )
                    generated_text = resp.choices[0].message.content
                    st.session_state.generated_need = generated_text
                    
                    st.markdown("##### ✅ 生成结果：")
                    st.info(generated_text)
                    
                    if st.button("📥 填入输入框", use_container_width=True, key="fill_btn"):
                        # 直接修改 session_state 中 text_area 对应的 key
                        st.session_state.need_input = generated_text
                        st.success("✅ 已填入输入框！")
                        
                except Exception as e:
                    st.error(f"生成失败: {str(e)}")
    
    # ===== 需求输入框 =====
    # 初始化
    if 'need_input' not in st.session_state:
        st.session_state.need_input = ""
    
    # 用 key 直接绑定，不写 value
    st.text_area(
        "📝 描述你的需求",
        height=120,
        placeholder="示例：我销售AI客服系统，目标客户是电商和零售公司，有客服团队，最近有融资或扩张计划。",
        key="need_input"
    )
    
    if st.button("🔍 开始搜索", use_container_width=True, type="primary"):
        # 从 session_state 读取
        need_description = st.session_state.get("need_input", "")
        if not need_description:
            st.error("⚠️ 请先输入需求描述")
        else:
            result_df = quick_search(need_description, mode_key)
            if not result_df.empty:
                result_df = result_df.sort_values("综合评分", ascending=False)
                
                st.markdown("---")
                st.markdown(f"##### 📊 搜索结果 · 共 {len(result_df)} 家公司")
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("🏢 公司总数", len(result_df))
                with col2:
                    st.metric("🔥 高优先级", len(result_df[result_df['优先级'].str.contains('高')]))
                with col3:
                    st.metric("📊 平均评分", int(result_df['综合评分'].mean()))
                with col4:
                    st.metric("📡 数据源", len(result_df['数据来源'].unique()))
                
                st.markdown("---")
                
                for _, row in result_df.iterrows():
                    score = row['综合评分']
                    priority = row['优先级']
                    p_class = "priority-high" if "高" in str(priority) else "priority-mid" if "中" in str(priority) else "priority-low"
                    p_label = "🔥 高优先级" if "高" in str(priority) else "📌 中优先级" if "中" in str(priority) else "💤 低优先级"
                    
                    st.markdown(f"""
                    <div class="company-card">
                        <div style="display:flex;justify-content:space-between;align-items:center;">
                            <div><strong>{row['公司名称']}</strong> <span class="{p_class}">{p_label}</span></div>
                            <div><span style="font-size:24px;font-weight:700;color:#667eea;">{score}</span></div>
                        </div>
                        <div style="margin-top:6px;display:flex;flex-wrap:wrap;gap:4px;">
                            <span class="tag">🎯 匹配度: {row.get('匹配度', 'N/A')}</span>
                            <span class="tag">📡 {row.get('数据来源', '')}</span>
                            {f'<span class="tag">👤 {row["创始人"]}</span>' if row.get('创始人') else ''}
                            {f'<span class="tag">📅 {row["成立时间"]}</span>' if row.get('成立时间') else ''}
                            {f'<span class="tag">💼 {row["招聘数"]}个岗位</span>' if row.get('招聘数', 0) > 0 else ''}
                        </div>
                        <div style="margin-top:6px;font-size:14px;color:#3c4043;">{row.get('理由', '')[:100]}</div>
                        <div style="font-size:13px;color:#667eea;">💡 {row.get('建议动作', '')}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                csv = result_df.to_csv(index=False).encode('utf-8-sig')
                st.download_button("📥 下载结果 (CSV)", data=csv, file_name=f"觅镜_结果_{datetime.now().strftime('%Y%m%d')}.csv", mime="text/csv", use_container_width=True)# ============================================================
# TAB 1: 发现引擎（修复版）
# ============================================================
with tab_main:
    st.markdown("##### 选择使用场景")
    
    if 'mode_selected' not in st.session_state:
        st.session_state.mode_selected = "销售"
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💼 销售模式\n找潜在客户", use_container_width=True, key="mode_sales"):
            st.session_state.mode_selected = "销售"
            st.rerun()
    with col2:
        if st.button("🎓 求职模式\n找理想雇主", use_container_width=True, key="mode_job"):
            st.session_state.mode_selected = "求职"
            st.rerun()
    
    mode_key = st.session_state.mode_selected
    st.markdown(f'<div style="background:linear-gradient(135deg,#667eea,#764ba2);color:white;padding:10px 20px;border-radius:10px;text-align:center;font-weight:600;margin:8px 0 12px 0;">✅ 当前模式：{"💼 销售" if mode_key == "销售" else "🎓 求职"}</div>', unsafe_allow_html=True)
    
    # ===== AI 帮你写需求 =====
    with st.expander("🤖 AI 帮我写需求描述", expanded=False):
        st.caption("💡 填写信息后点击生成，AI 会自动生成需求描述，然后点击「填入输入框」")
        
        if mode_key == "销售":
            col_a, col_b = st.columns(2)
            with col_a:
                product = st.text_input("产品/服务", placeholder="AI客服系统", key="p1")
                target_industry = st.text_input("目标行业", placeholder="电商", key="p2")
            with col_b:
                target_size = st.text_input("目标规模", placeholder="500人以上", key="p3")
                pain_point = st.text_input("客户痛点", placeholder="客服响应慢", key="p4")
            extra = st.text_area("补充信息", placeholder="最近有融资的优先", key="p5", height=40)
        else:
            col_a, col_b = st.columns(2)
            with col_a:
                skill = st.text_input("核心技能", placeholder="前端开发", key="j1")
                tech_stack = st.text_input("技术栈", placeholder="React, TypeScript", key="j2")
            with col_b:
                target_industry_job = st.text_input("目标行业", placeholder="互联网", key="j3")
                job_level = st.text_input("目标职级", placeholder="中级", key="j4")
            extra = st.text_area("补充信息", placeholder="希望公司已盈利", key="j5", height=40)
        
        if st.button("🚀 生成需求描述", use_container_width=True, key="gen_btn"):
            if mode_key == "销售":
                info = f"产品：{product or '未填写'}\n行业：{target_industry or '未填写'}\n规模：{target_size or '未填写'}\n痛点：{pain_point or '未填写'}\n补充：{extra or '无'}"
                prompt_text = f"你是商业需求分析师。生成一段专业完整的需求描述（150-200字）。用户信息：\n{info}\n要求：直接输出描述，不要有其他内容。"
            else:
                info = f"技能：{skill or '未填写'}\n技术栈：{tech_stack or '未填写'}\n目标行业：{target_industry_job or '未填写'}\n职级：{job_level or '未填写'}\n补充：{extra or '无'}"
                prompt_text = f"你是职业规划师。生成一段专业完整的求职需求描述（150-200字）。用户信息：\n{info}\n要求：直接输出描述，不要有其他内容。"
            
            with st.spinner("🤖 AI 生成中..."):
                try:
                    resp = client.chat.completions.create(
                        model="deepseek-chat",
                        messages=[{"role": "system", "content": "你是专业文案助手。"}, {"role": "user", "content": prompt_text}],
                        temperature=0.7,
                        max_tokens=800
                    )
                    generated_text = resp.choices[0].message.content
                    st.session_state.generated_need = generated_text
                    
                    st.markdown("##### ✅ 生成结果：")
                    st.info(generated_text)
                    
                    if st.button("📥 填入输入框", use_container_width=True, key="fill_btn"):
                        # 直接修改 session_state 中 text_area 对应的 key
                        st.session_state.need_input = generated_text
                        st.success("✅ 已填入输入框！")
                        
                except Exception as e:
                    st.error(f"生成失败: {str(e)}")
    
    # ===== 需求输入框 =====
    # 初始化
    if 'need_input' not in st.session_state:
        st.session_state.need_input = ""
    
    # 用 key 直接绑定，不写 value
    st.text_area(
        "📝 描述你的需求",
        height=120,
        placeholder="示例：我销售AI客服系统，目标客户是电商和零售公司，有客服团队，最近有融资或扩张计划。",
        key="need_input"
    )
    
    if st.button("🔍 开始搜索", use_container_width=True, type="primary"):
        # 从 session_state 读取
        need_description = st.session_state.get("need_input", "")
        if not need_description:
            st.error("⚠️ 请先输入需求描述")
        else:
            result_df = quick_search(need_description, mode_key)
            if not result_df.empty:
                result_df = result_df.sort_values("综合评分", ascending=False)
                
                st.markdown("---")
                st.markdown(f"##### 📊 搜索结果 · 共 {len(result_df)} 家公司")
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("🏢 公司总数", len(result_df))
                with col2:
                    st.metric("🔥 高优先级", len(result_df[result_df['优先级'].str.contains('高')]))
                with col3:
                    st.metric("📊 平均评分", int(result_df['综合评分'].mean()))
                with col4:
                    st.metric("📡 数据源", len(result_df['数据来源'].unique()))
                
                st.markdown("---")
                
                for _, row in result_df.iterrows():
                    score = row['综合评分']
                    priority = row['优先级']
                    p_class = "priority-high" if "高" in str(priority) else "priority-mid" if "中" in str(priority) else "priority-low"
                    p_label = "🔥 高优先级" if "高" in str(priority) else "📌 中优先级" if "中" in str(priority) else "💤 低优先级"
                    
                    st.markdown(f"""
                    <div class="company-card">
                        <div style="display:flex;justify-content:space-between;align-items:center;">
                            <div><strong>{row['公司名称']}</strong> <span class="{p_class}">{p_label}</span></div>
                            <div><span style="font-size:24px;font-weight:700;color:#667eea;">{score}</span></div>
                        </div>
                        <div style="margin-top:6px;display:flex;flex-wrap:wrap;gap:4px;">
                            <span class="tag">🎯 匹配度: {row.get('匹配度', 'N/A')}</span>
                            <span class="tag">📡 {row.get('数据来源', '')}</span>
                            {f'<span class="tag">👤 {row["创始人"]}</span>' if row.get('创始人') else ''}
                            {f'<span class="tag">📅 {row["成立时间"]}</span>' if row.get('成立时间') else ''}
                            {f'<span class="tag">💼 {row["招聘数"]}个岗位</span>' if row.get('招聘数', 0) > 0 else ''}
                        </div>
                        <div style="margin-top:6px;font-size:14px;color:#3c4043;">{row.get('理由', '')[:100]}</div>
                        <div style="font-size:13px;color:#667eea;">💡 {row.get('建议动作', '')}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                csv = result_df.to_csv(index=False).encode('utf-8-sig')
                st.download_button("📥 下载结果 (CSV)", data=csv, file_name=f"觅镜_结果_{datetime.now().strftime('%Y%m%d')}.csv", mime="text/csv", use_container_width=True)# ============================================================
# TAB 1: 发现引擎（修复版）
# ============================================================
with tab_main:
    st.markdown("##### 选择使用场景")
    
    if 'mode_selected' not in st.session_state:
        st.session_state.mode_selected = "销售"
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💼 销售模式\n找潜在客户", use_container_width=True, key="mode_sales"):
            st.session_state.mode_selected = "销售"
            st.rerun()
    with col2:
        if st.button("🎓 求职模式\n找理想雇主", use_container_width=True, key="mode_job"):
            st.session_state.mode_selected = "求职"
            st.rerun()
    
    mode_key = st.session_state.mode_selected
    st.markdown(f'<div style="background:linear-gradient(135deg,#667eea,#764ba2);color:white;padding:10px 20px;border-radius:10px;text-align:center;font-weight:600;margin:8px 0 12px 0;">✅ 当前模式：{"💼 销售" if mode_key == "销售" else "🎓 求职"}</div>', unsafe_allow_html=True)
    
    # ===== AI 帮你写需求 =====
    with st.expander("🤖 AI 帮我写需求描述", expanded=False):
        st.caption("💡 填写信息后点击生成，AI 会自动生成需求描述，然后点击「填入输入框」")
        
        if mode_key == "销售":
            col_a, col_b = st.columns(2)
            with col_a:
                product = st.text_input("产品/服务", placeholder="AI客服系统", key="p1")
                target_industry = st.text_input("目标行业", placeholder="电商", key="p2")
            with col_b:
                target_size = st.text_input("目标规模", placeholder="500人以上", key="p3")
                pain_point = st.text_input("客户痛点", placeholder="客服响应慢", key="p4")
            extra = st.text_area("补充信息", placeholder="最近有融资的优先", key="p5", height=40)
        else:
            col_a, col_b = st.columns(2)
            with col_a:
                skill = st.text_input("核心技能", placeholder="前端开发", key="j1")
                tech_stack = st.text_input("技术栈", placeholder="React, TypeScript", key="j2")
            with col_b:
                target_industry_job = st.text_input("目标行业", placeholder="互联网", key="j3")
                job_level = st.text_input("目标职级", placeholder="中级", key="j4")
            extra = st.text_area("补充信息", placeholder="希望公司已盈利", key="j5", height=40)
        
        if st.button("🚀 生成需求描述", use_container_width=True, key="gen_btn"):
            if mode_key == "销售":
                info = f"产品：{product or '未填写'}\n行业：{target_industry or '未填写'}\n规模：{target_size or '未填写'}\n痛点：{pain_point or '未填写'}\n补充：{extra or '无'}"
                prompt_text = f"你是商业需求分析师。生成一段专业完整的需求描述（150-200字）。用户信息：\n{info}\n要求：直接输出描述，不要有其他内容。"
            else:
                info = f"技能：{skill or '未填写'}\n技术栈：{tech_stack or '未填写'}\n目标行业：{target_industry_job or '未填写'}\n职级：{job_level or '未填写'}\n补充：{extra or '无'}"
                prompt_text = f"你是职业规划师。生成一段专业完整的求职需求描述（150-200字）。用户信息：\n{info}\n要求：直接输出描述，不要有其他内容。"
            
            with st.spinner("🤖 AI 生成中..."):
                try:
                    resp = client.chat.completions.create(
                        model="deepseek-chat",
                        messages=[{"role": "system", "content": "你是专业文案助手。"}, {"role": "user", "content": prompt_text}],
                        temperature=0.7,
                        max_tokens=800
                    )
                    generated_text = resp.choices[0].message.content
                    st.session_state.generated_need = generated_text
                    
                    st.markdown("##### ✅ 生成结果：")
                    st.info(generated_text)
                    
                    if st.button("📥 填入输入框", use_container_width=True, key="fill_btn"):
                        # 直接修改 session_state 中 text_area 对应的 key
                        st.session_state.need_input = generated_text
                        st.success("✅ 已填入输入框！")
                        
                except Exception as e:
                    st.error(f"生成失败: {str(e)}")
    
    # ===== 需求输入框 =====
    # 初始化
    if 'need_input' not in st.session_state:
        st.session_state.need_input = ""
    
    # 用 key 直接绑定，不写 value
    st.text_area(
        "📝 描述你的需求",
        height=120,
        placeholder="示例：我销售AI客服系统，目标客户是电商和零售公司，有客服团队，最近有融资或扩张计划。",
        key="need_input"
    )
    
    if st.button("🔍 开始搜索", use_container_width=True, type="primary"):
        # 从 session_state 读取
        need_description = st.session_state.get("need_input", "")
        if not need_description:
            st.error("⚠️ 请先输入需求描述")
        else:
            result_df = quick_search(need_description, mode_key)
            if not result_df.empty:
                result_df = result_df.sort_values("综合评分", ascending=False)
                
                st.markdown("---")
                st.markdown(f"##### 📊 搜索结果 · 共 {len(result_df)} 家公司")
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("🏢 公司总数", len(result_df))
                with col2:
                    st.metric("🔥 高优先级", len(result_df[result_df['优先级'].str.contains('高')]))
                with col3:
                    st.metric("📊 平均评分", int(result_df['综合评分'].mean()))
                with col4:
                    st.metric("📡 数据源", len(result_df['数据来源'].unique()))
                
                st.markdown("---")
                
                for _, row in result_df.iterrows():
                    score = row['综合评分']
                    priority = row['优先级']
                    p_class = "priority-high" if "高" in str(priority) else "priority-mid" if "中" in str(priority) else "priority-low"
                    p_label = "🔥 高优先级" if "高" in str(priority) else "📌 中优先级" if "中" in str(priority) else "💤 低优先级"
                    
                    st.markdown(f"""
                    <div class="company-card">
                        <div style="display:flex;justify-content:space-between;align-items:center;">
                            <div><strong>{row['公司名称']}</strong> <span class="{p_class}">{p_label}</span></div>
                            <div><span style="font-size:24px;font-weight:700;color:#667eea;">{score}</span></div>
                        </div>
                        <div style="margin-top:6px;display:flex;flex-wrap:wrap;gap:4px;">
                            <span class="tag">🎯 匹配度: {row.get('匹配度', 'N/A')}</span>
                            <span class="tag">📡 {row.get('数据来源', '')}</span>
                            {f'<span class="tag">👤 {row["创始人"]}</span>' if row.get('创始人') else ''}
                            {f'<span class="tag">📅 {row["成立时间"]}</span>' if row.get('成立时间') else ''}
                            {f'<span class="tag">💼 {row["招聘数"]}个岗位</span>' if row.get('招聘数', 0) > 0 else ''}
                        </div>
                        <div style="margin-top:6px;font-size:14px;color:#3c4043;">{row.get('理由', '')[:100]}</div>
                        <div style="font-size:13px;color:#667eea;">💡 {row.get('建议动作', '')}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                csv = result_df.to_csv(index=False).encode('utf-8-sig')
                st.download_button("📥 下载结果 (CSV)", data=csv, file_name=f"觅镜_结果_{datetime.now().strftime('%Y%m%d')}.csv", mime="text/csv", use_container_width=True)# ============================================================
# TAB 1: 发现引擎（修复版）
# ============================================================
with tab_main:
    st.markdown("##### 选择使用场景")
    
    if 'mode_selected' not in st.session_state:
        st.session_state.mode_selected = "销售"
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💼 销售模式\n找潜在客户", use_container_width=True, key="mode_sales"):
            st.session_state.mode_selected = "销售"
            st.rerun()
    with col2:
        if st.button("🎓 求职模式\n找理想雇主", use_container_width=True, key="mode_job"):
            st.session_state.mode_selected = "求职"
            st.rerun()
    
    mode_key = st.session_state.mode_selected
    st.markdown(f'<div style="background:linear-gradient(135deg,#667eea,#764ba2);color:white;padding:10px 20px;border-radius:10px;text-align:center;font-weight:600;margin:8px 0 12px 0;">✅ 当前模式：{"💼 销售" if mode_key == "销售" else "🎓 求职"}</div>', unsafe_allow_html=True)
    
    # ===== AI 帮你写需求 =====
    with st.expander("🤖 AI 帮我写需求描述", expanded=False):
        st.caption("💡 填写信息后点击生成，AI 会自动生成需求描述，然后点击「填入输入框」")
        
        if mode_key == "销售":
            col_a, col_b = st.columns(2)
            with col_a:
                product = st.text_input("产品/服务", placeholder="AI客服系统", key="p1")
                target_industry = st.text_input("目标行业", placeholder="电商", key="p2")
            with col_b:
                target_size = st.text_input("目标规模", placeholder="500人以上", key="p3")
                pain_point = st.text_input("客户痛点", placeholder="客服响应慢", key="p4")
            extra = st.text_area("补充信息", placeholder="最近有融资的优先", key="p5", height=40)
        else:
            col_a, col_b = st.columns(2)
            with col_a:
                skill = st.text_input("核心技能", placeholder="前端开发", key="j1")
                tech_stack = st.text_input("技术栈", placeholder="React, TypeScript", key="j2")
            with col_b:
                target_industry_job = st.text_input("目标行业", placeholder="互联网", key="j3")
                job_level = st.text_input("目标职级", placeholder="中级", key="j4")
            extra = st.text_area("补充信息", placeholder="希望公司已盈利", key="j5", height=40)
        
        if st.button("🚀 生成需求描述", use_container_width=True, key="gen_btn"):
            if mode_key == "销售":
                info = f"产品：{product or '未填写'}\n行业：{target_industry or '未填写'}\n规模：{target_size or '未填写'}\n痛点：{pain_point or '未填写'}\n补充：{extra or '无'}"
                prompt_text = f"你是商业需求分析师。生成一段专业完整的需求描述（150-200字）。用户信息：\n{info}\n要求：直接输出描述，不要有其他内容。"
            else:
                info = f"技能：{skill or '未填写'}\n技术栈：{tech_stack or '未填写'}\n目标行业：{target_industry_job or '未填写'}\n职级：{job_level or '未填写'}\n补充：{extra or '无'}"
                prompt_text = f"你是职业规划师。生成一段专业完整的求职需求描述（150-200字）。用户信息：\n{info}\n要求：直接输出描述，不要有其他内容。"
            
            with st.spinner("🤖 AI 生成中..."):
                try:
                    resp = client.chat.completions.create(
                        model="deepseek-chat",
                        messages=[{"role": "system", "content": "你是专业文案助手。"}, {"role": "user", "content": prompt_text}],
                        temperature=0.7,
                        max_tokens=800
                    )
                    generated_text = resp.choices[0].message.content
                    st.session_state.generated_need = generated_text
                    
                    st.markdown("##### ✅ 生成结果：")
                    st.info(generated_text)
                    
                    if st.button("📥 填入输入框", use_container_width=True, key="fill_btn"):
                        # 直接修改 session_state 中 text_area 对应的 key
                        st.session_state.need_input = generated_text
                        st.success("✅ 已填入输入框！")
                        
                except Exception as e:
                    st.error(f"生成失败: {str(e)}")
    
    # ===== 需求输入框 =====
    # 初始化
    if 'need_input' not in st.session_state:
        st.session_state.need_input = ""
    
    # 用 key 直接绑定，不写 value
    st.text_area(
        "📝 描述你的需求",
        height=120,
        placeholder="示例：我销售AI客服系统，目标客户是电商和零售公司，有客服团队，最近有融资或扩张计划。",
        key="need_input"
    )
    
    if st.button("🔍 开始搜索", use_container_width=True, type="primary"):
        # 从 session_state 读取
        need_description = st.session_state.get("need_input", "")
        if not need_description:
            st.error("⚠️ 请先输入需求描述")
        else:
            result_df = quick_search(need_description, mode_key)
            if not result_df.empty:
                result_df = result_df.sort_values("综合评分", ascending=False)
                
                st.markdown("---")
                st.markdown(f"##### 📊 搜索结果 · 共 {len(result_df)} 家公司")
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("🏢 公司总数", len(result_df))
                with col2:
                    st.metric("🔥 高优先级", len(result_df[result_df['优先级'].str.contains('高')]))
                with col3:
                    st.metric("📊 平均评分", int(result_df['综合评分'].mean()))
                with col4:
                    st.metric("📡 数据源", len(result_df['数据来源'].unique()))
                
                st.markdown("---")
                
                for _, row in result_df.iterrows():
                    score = row['综合评分']
                    priority = row['优先级']
                    p_class = "priority-high" if "高" in str(priority) else "priority-mid" if "中" in str(priority) else "priority-low"
                    p_label = "🔥 高优先级" if "高" in str(priority) else "📌 中优先级" if "中" in str(priority) else "💤 低优先级"
                    
                    st.markdown(f"""
                    <div class="company-card">
                        <div style="display:flex;justify-content:space-between;align-items:center;">
                            <div><strong>{row['公司名称']}</strong> <span class="{p_class}">{p_label}</span></div>
                            <div><span style="font-size:24px;font-weight:700;color:#667eea;">{score}</span></div>
                        </div>
                        <div style="margin-top:6px;display:flex;flex-wrap:wrap;gap:4px;">
                            <span class="tag">🎯 匹配度: {row.get('匹配度', 'N/A')}</span>
                            <span class="tag">📡 {row.get('数据来源', '')}</span>
                            {f'<span class="tag">👤 {row["创始人"]}</span>' if row.get('创始人') else ''}
                            {f'<span class="tag">📅 {row["成立时间"]}</span>' if row.get('成立时间') else ''}
                            {f'<span class="tag">💼 {row["招聘数"]}个岗位</span>' if row.get('招聘数', 0) > 0 else ''}
                        </div>
                        <div style="margin-top:6px;font-size:14px;color:#3c4043;">{row.get('理由', '')[:100]}</div>
                        <div style="font-size:13px;color:#667eea;">💡 {row.get('建议动作', '')}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                csv = result_df.to_csv(index=False).encode('utf-8-sig')
                st.download_button("📥 下载结果 (CSV)", data=csv, file_name=f"觅镜_结果_{datetime.now().strftime('%Y%m%d')}.csv", mime="text/csv", use_container_width=True)# ============================================================
# TAB 1: 发现引擎（修复版）
# ============================================================
with tab_main:
    st.markdown("##### 选择使用场景")
    
    if 'mode_selected' not in st.session_state:
        st.session_state.mode_selected = "销售"
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💼 销售模式\n找潜在客户", use_container_width=True, key="mode_sales"):
            st.session_state.mode_selected = "销售"
            st.rerun()
    with col2:
        if st.button("🎓 求职模式\n找理想雇主", use_container_width=True, key="mode_job"):
            st.session_state.mode_selected = "求职"
            st.rerun()
    
    mode_key = st.session_state.mode_selected
    st.markdown(f'<div style="background:linear-gradient(135deg,#667eea,#764ba2);color:white;padding:10px 20px;border-radius:10px;text-align:center;font-weight:600;margin:8px 0 12px 0;">✅ 当前模式：{"💼 销售" if mode_key == "销售" else "🎓 求职"}</div>', unsafe_allow_html=True)
    
    # ===== AI 帮你写需求 =====
    with st.expander("🤖 AI 帮我写需求描述", expanded=False):
        st.caption("💡 填写信息后点击生成，AI 会自动生成需求描述，然后点击「填入输入框」")
        
        if mode_key == "销售":
            col_a, col_b = st.columns(2)
            with col_a:
                product = st.text_input("产品/服务", placeholder="AI客服系统", key="p1")
                target_industry = st.text_input("目标行业", placeholder="电商", key="p2")
            with col_b:
                target_size = st.text_input("目标规模", placeholder="500人以上", key="p3")
                pain_point = st.text_input("客户痛点", placeholder="客服响应慢", key="p4")
            extra = st.text_area("补充信息", placeholder="最近有融资的优先", key="p5", height=40)
        else:
            col_a, col_b = st.columns(2)
            with col_a:
                skill = st.text_input("核心技能", placeholder="前端开发", key="j1")
                tech_stack = st.text_input("技术栈", placeholder="React, TypeScript", key="j2")
            with col_b:
                target_industry_job = st.text_input("目标行业", placeholder="互联网", key="j3")
                job_level = st.text_input("目标职级", placeholder="中级", key="j4")
            extra = st.text_area("补充信息", placeholder="希望公司已盈利", key="j5", height=40)
        
        if st.button("🚀 生成需求描述", use_container_width=True, key="gen_btn"):
            if mode_key == "销售":
                info = f"产品：{product or '未填写'}\n行业：{target_industry or '未填写'}\n规模：{target_size or '未填写'}\n痛点：{pain_point or '未填写'}\n补充：{extra or '无'}"
                prompt_text = f"你是商业需求分析师。生成一段专业完整的需求描述（150-200字）。用户信息：\n{info}\n要求：直接输出描述，不要有其他内容。"
            else:
                info = f"技能：{skill or '未填写'}\n技术栈：{tech_stack or '未填写'}\n目标行业：{target_industry_job or '未填写'}\n职级：{job_level or '未填写'}\n补充：{extra or '无'}"
                prompt_text = f"你是职业规划师。生成一段专业完整的求职需求描述（150-200字）。用户信息：\n{info}\n要求：直接输出描述，不要有其他内容。"
            
            with st.spinner("🤖 AI 生成中..."):
                try:
                    resp = client.chat.completions.create(
                        model="deepseek-chat",
                        messages=[{"role": "system", "content": "你是专业文案助手。"}, {"role": "user", "content": prompt_text}],
                        temperature=0.7,
                        max_tokens=800
                    )
                    generated_text = resp.choices[0].message.content
                    st.session_state.generated_need = generated_text
                    
                    st.markdown("##### ✅ 生成结果：")
                    st.info(generated_text)
                    
                    if st.button("📥 填入输入框", use_container_width=True, key="fill_btn"):
                        # 直接修改 session_state 中 text_area 对应的 key
                        st.session_state.need_input = generated_text
                        st.success("✅ 已填入输入框！")
                        
                except Exception as e:
                    st.error(f"生成失败: {str(e)}")
    
    # ===== 需求输入框 =====
    # 初始化
    if 'need_input' not in st.session_state:
        st.session_state.need_input = ""
    
    # 用 key 直接绑定，不写 value
    st.text_area(
        "📝 描述你的需求",
        height=120,
        placeholder="示例：我销售AI客服系统，目标客户是电商和零售公司，有客服团队，最近有融资或扩张计划。",
        key="need_input"
    )
    
    if st.button("🔍 开始搜索", use_container_width=True, type="primary"):
        # 从 session_state 读取
        need_description = st.session_state.get("need_input", "")
        if not need_description:
            st.error("⚠️ 请先输入需求描述")
        else:
            result_df = quick_search(need_description, mode_key)
            if not result_df.empty:
                result_df = result_df.sort_values("综合评分", ascending=False)
                
                st.markdown("---")
                st.markdown(f"##### 📊 搜索结果 · 共 {len(result_df)} 家公司")
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("🏢 公司总数", len(result_df))
                with col2:
                    st.metric("🔥 高优先级", len(result_df[result_df['优先级'].str.contains('高')]))
                with col3:
                    st.metric("📊 平均评分", int(result_df['综合评分'].mean()))
                with col4:
                    st.metric("📡 数据源", len(result_df['数据来源'].unique()))
                
                st.markdown("---")
                
                for _, row in result_df.iterrows():
                    score = row['综合评分']
                    priority = row['优先级']
                    p_class = "priority-high" if "高" in str(priority) else "priority-mid" if "中" in str(priority) else "priority-low"
                    p_label = "🔥 高优先级" if "高" in str(priority) else "📌 中优先级" if "中" in str(priority) else "💤 低优先级"
                    
                    st.markdown(f"""
                    <div class="company-card">
                        <div style="display:flex;justify-content:space-between;align-items:center;">
                            <div><strong>{row['公司名称']}</strong> <span class="{p_class}">{p_label}</span></div>
                            <div><span style="font-size:24px;font-weight:700;color:#667eea;">{score}</span></div>
                        </div>
                        <div style="margin-top:6px;display:flex;flex-wrap:wrap;gap:4px;">
                            <span class="tag">🎯 匹配度: {row.get('匹配度', 'N/A')}</span>
                            <span class="tag">📡 {row.get('数据来源', '')}</span>
                            {f'<span class="tag">👤 {row["创始人"]}</span>' if row.get('创始人') else ''}
                            {f'<span class="tag">📅 {row["成立时间"]}</span>' if row.get('成立时间') else ''}
                            {f'<span class="tag">💼 {row["招聘数"]}个岗位</span>' if row.get('招聘数', 0) > 0 else ''}
                        </div>
                        <div style="margin-top:6px;font-size:14px;color:#3c4043;">{row.get('理由', '')[:100]}</div>
                        <div style="font-size:13px;color:#667eea;">💡 {row.get('建议动作', '')}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                csv = result_df.to_csv(index=False).encode('utf-8-sig')
                st.download_button("📥 下载结果 (CSV)", data=csv, file_name=f"觅镜_结果_{datetime.now().strftime('%Y%m%d')}.csv", mime="text/csv", use_container_width=True)# ============================================================
# TAB 1: 发现引擎（修复版）
# ============================================================
with tab_main:
    st.markdown("##### 选择使用场景")
    
    if 'mode_selected' not in st.session_state:
        st.session_state.mode_selected = "销售"
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💼 销售模式\n找潜在客户", use_container_width=True, key="mode_sales"):
            st.session_state.mode_selected = "销售"
            st.rerun()
    with col2:
        if st.button("🎓 求职模式\n找理想雇主", use_container_width=True, key="mode_job"):
            st.session_state.mode_selected = "求职"
            st.rerun()
    
    mode_key = st.session_state.mode_selected
    st.markdown(f'<div style="background:linear-gradient(135deg,#667eea,#764ba2);color:white;padding:10px 20px;border-radius:10px;text-align:center;font-weight:600;margin:8px 0 12px 0;">✅ 当前模式：{"💼 销售" if mode_key == "销售" else "🎓 求职"}</div>', unsafe_allow_html=True)
    
    # ===== AI 帮你写需求 =====
    with st.expander("🤖 AI 帮我写需求描述", expanded=False):
        st.caption("💡 填写信息后点击生成，AI 会自动生成需求描述，然后点击「填入输入框」")
        
        if mode_key == "销售":
            col_a, col_b = st.columns(2)
            with col_a:
                product = st.text_input("产品/服务", placeholder="AI客服系统", key="p1")
                target_industry = st.text_input("目标行业", placeholder="电商", key="p2")
            with col_b:
                target_size = st.text_input("目标规模", placeholder="500人以上", key="p3")
                pain_point = st.text_input("客户痛点", placeholder="客服响应慢", key="p4")
            extra = st.text_area("补充信息", placeholder="最近有融资的优先", key="p5", height=40)
        else:
            col_a, col_b = st.columns(2)
            with col_a:
                skill = st.text_input("核心技能", placeholder="前端开发", key="j1")
                tech_stack = st.text_input("技术栈", placeholder="React, TypeScript", key="j2")
            with col_b:
                target_industry_job = st.text_input("目标行业", placeholder="互联网", key="j3")
                job_level = st.text_input("目标职级", placeholder="中级", key="j4")
            extra = st.text_area("补充信息", placeholder="希望公司已盈利", key="j5", height=40)
        
        if st.button("🚀 生成需求描述", use_container_width=True, key="gen_btn"):
            if mode_key == "销售":
                info = f"产品：{product or '未填写'}\n行业：{target_industry or '未填写'}\n规模：{target_size or '未填写'}\n痛点：{pain_point or '未填写'}\n补充：{extra or '无'}"
                prompt_text = f"你是商业需求分析师。生成一段专业完整的需求描述（150-200字）。用户信息：\n{info}\n要求：直接输出描述，不要有其他内容。"
            else:
                info = f"技能：{skill or '未填写'}\n技术栈：{tech_stack or '未填写'}\n目标行业：{target_industry_job or '未填写'}\n职级：{job_level or '未填写'}\n补充：{extra or '无'}"
                prompt_text = f"你是职业规划师。生成一段专业完整的求职需求描述（150-200字）。用户信息：\n{info}\n要求：直接输出描述，不要有其他内容。"
            
            with st.spinner("🤖 AI 生成中..."):
                try:
                    resp = client.chat.completions.create(
                        model="deepseek-chat",
                        messages=[{"role": "system", "content": "你是专业文案助手。"}, {"role": "user", "content": prompt_text}],
                        temperature=0.7,
                        max_tokens=800
                    )
                    generated_text = resp.choices[0].message.content
                    st.session_state.generated_need = generated_text
                    
                    st.markdown("##### ✅ 生成结果：")
                    st.info(generated_text)
                    
                    if st.button("📥 填入输入框", use_container_width=True, key="fill_btn"):
                        # 直接修改 session_state 中 text_area 对应的 key
                        st.session_state.need_input = generated_text
                        st.success("✅ 已填入输入框！")
                        
                except Exception as e:
                    st.error(f"生成失败: {str(e)}")
    
    # ===== 需求输入框 =====
    # 初始化
    if 'need_input' not in st.session_state:
        st.session_state.need_input = ""
    
    # 用 key 直接绑定，不写 value
    st.text_area(
        "📝 描述你的需求",
        height=120,
        placeholder="示例：我销售AI客服系统，目标客户是电商和零售公司，有客服团队，最近有融资或扩张计划。",
        key="need_input"
    )
    
    if st.button("🔍 开始搜索", use_container_width=True, type="primary"):
        # 从 session_state 读取
        need_description = st.session_state.get("need_input", "")
        if not need_description:
            st.error("⚠️ 请先输入需求描述")
        else:
            result_df = quick_search(need_description, mode_key)
            if not result_df.empty:
                result_df = result_df.sort_values("综合评分", ascending=False)
                
                st.markdown("---")
                st.markdown(f"##### 📊 搜索结果 · 共 {len(result_df)} 家公司")
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("🏢 公司总数", len(result_df))
                with col2:
                    st.metric("🔥 高优先级", len(result_df[result_df['优先级'].str.contains('高')]))
                with col3:
                    st.metric("📊 平均评分", int(result_df['综合评分'].mean()))
                with col4:
                    st.metric("📡 数据源", len(result_df['数据来源'].unique()))
                
                st.markdown("---")
                
                for _, row in result_df.iterrows():
                    score = row['综合评分']
                    priority = row['优先级']
                    p_class = "priority-high" if "高" in str(priority) else "priority-mid" if "中" in str(priority) else "priority-low"
                    p_label = "🔥 高优先级" if "高" in str(priority) else "📌 中优先级" if "中" in str(priority) else "💤 低优先级"
                    
                    st.markdown(f"""
                    <div class="company-card">
                        <div style="display:flex;justify-content:space-between;align-items:center;">
                            <div><strong>{row['公司名称']}</strong> <span class="{p_class}">{p_label}</span></div>
                            <div><span style="font-size:24px;font-weight:700;color:#667eea;">{score}</span></div>
                        </div>
                        <div style="margin-top:6px;display:flex;flex-wrap:wrap;gap:4px;">
                            <span class="tag">🎯 匹配度: {row.get('匹配度', 'N/A')}</span>
                            <span class="tag">📡 {row.get('数据来源', '')}</span>
                            {f'<span class="tag">👤 {row["创始人"]}</span>' if row.get('创始人') else ''}
                            {f'<span class="tag">📅 {row["成立时间"]}</span>' if row.get('成立时间') else ''}
                            {f'<span class="tag">💼 {row["招聘数"]}个岗位</span>' if row.get('招聘数', 0) > 0 else ''}
                        </div>
                        <div style="margin-top:6px;font-size:14px;color:#3c4043;">{row.get('理由', '')[:100]}</div>
                        <div style="font-size:13px;color:#667eea;">💡 {row.get('建议动作', '')}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                csv = result_df.to_csv(index=False).encode('utf-8-sig')
                st.download_button("📥 下载结果 (CSV)", data=csv, file_name=f"觅镜_结果_{datetime.now().strftime('%Y%m%d')}.csv", mime="text/csv", use_container_width=True)# ============================================================
# TAB 1: 发现引擎（修复版）
# ============================================================
with tab_main:
    st.markdown("##### 选择使用场景")
    
    if 'mode_selected' not in st.session_state:
        st.session_state.mode_selected = "销售"
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💼 销售模式\n找潜在客户", use_container_width=True, key="mode_sales"):
            st.session_state.mode_selected = "销售"
            st.rerun()
    with col2:
        if st.button("🎓 求职模式\n找理想雇主", use_container_width=True, key="mode_job"):
            st.session_state.mode_selected = "求职"
            st.rerun()
    
    mode_key = st.session_state.mode_selected
    st.markdown(f'<div style="background:linear-gradient(135deg,#667eea,#764ba2);color:white;padding:10px 20px;border-radius:10px;text-align:center;font-weight:600;margin:8px 0 12px 0;">✅ 当前模式：{"💼 销售" if mode_key == "销售" else "🎓 求职"}</div>', unsafe_allow_html=True)
    
    # ===== AI 帮你写需求 =====
    with st.expander("🤖 AI 帮我写需求描述", expanded=False):
        st.caption("💡 填写信息后点击生成，AI 会自动生成需求描述，然后点击「填入输入框」")
        
        if mode_key == "销售":
            col_a, col_b = st.columns(2)
            with col_a:
                product = st.text_input("产品/服务", placeholder="AI客服系统", key="p1")
                target_industry = st.text_input("目标行业", placeholder="电商", key="p2")
            with col_b:
                target_size = st.text_input("目标规模", placeholder="500人以上", key="p3")
                pain_point = st.text_input("客户痛点", placeholder="客服响应慢", key="p4")
            extra = st.text_area("补充信息", placeholder="最近有融资的优先", key="p5", height=40)
        else:
            col_a, col_b = st.columns(2)
            with col_a:
                skill = st.text_input("核心技能", placeholder="前端开发", key="j1")
                tech_stack = st.text_input("技术栈", placeholder="React, TypeScript", key="j2")
            with col_b:
                target_industry_job = st.text_input("目标行业", placeholder="互联网", key="j3")
                job_level = st.text_input("目标职级", placeholder="中级", key="j4")
            extra = st.text_area("补充信息", placeholder="希望公司已盈利", key="j5", height=40)
        
        if st.button("🚀 生成需求描述", use_container_width=True, key="gen_btn"):
            if mode_key == "销售":
                info = f"产品：{product or '未填写'}\n行业：{target_industry or '未填写'}\n规模：{target_size or '未填写'}\n痛点：{pain_point or '未填写'}\n补充：{extra or '无'}"
                prompt_text = f"你是商业需求分析师。生成一段专业完整的需求描述（150-200字）。用户信息：\n{info}\n要求：直接输出描述，不要有其他内容。"
            else:
                info = f"技能：{skill or '未填写'}\n技术栈：{tech_stack or '未填写'}\n目标行业：{target_industry_job or '未填写'}\n职级：{job_level or '未填写'}\n补充：{extra or '无'}"
                prompt_text = f"你是职业规划师。生成一段专业完整的求职需求描述（150-200字）。用户信息：\n{info}\n要求：直接输出描述，不要有其他内容。"
            
            with st.spinner("🤖 AI 生成中..."):
                try:
                    resp = client.chat.completions.create(
                        model="deepseek-chat",
                        messages=[{"role": "system", "content": "你是专业文案助手。"}, {"role": "user", "content": prompt_text}],
                        temperature=0.7,
                        max_tokens=800
                    )
                    generated_text = resp.choices[0].message.content
                    st.session_state.generated_need = generated_text
                    
                    st.markdown("##### ✅ 生成结果：")
                    st.info(generated_text)
                    
                    if st.button("📥 填入输入框", use_container_width=True, key="fill_btn"):
                        # 直接修改 session_state 中 text_area 对应的 key
                        st.session_state.need_input = generated_text
                        st.success("✅ 已填入输入框！")
                        
                except Exception as e:
                    st.error(f"生成失败: {str(e)}")
    
    # ===== 需求输入框 =====
    # 初始化
    if 'need_input' not in st.session_state:
        st.session_state.need_input = ""
    
    # 用 key 直接绑定，不写 value
    st.text_area(
        "📝 描述你的需求",
        height=120,
        placeholder="示例：我销售AI客服系统，目标客户是电商和零售公司，有客服团队，最近有融资或扩张计划。",
        key="need_input"
    )
    
    if st.button("🔍 开始搜索", use_container_width=True, type="primary"):
        # 从 session_state 读取
        need_description = st.session_state.get("need_input", "")
        if not need_description:
            st.error("⚠️ 请先输入需求描述")
        else:
            result_df = quick_search(need_description, mode_key)
            if not result_df.empty:
                result_df = result_df.sort_values("综合评分", ascending=False)
                
                st.markdown("---")
                st.markdown(f"##### 📊 搜索结果 · 共 {len(result_df)} 家公司")
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("🏢 公司总数", len(result_df))
                with col2:
                    st.metric("🔥 高优先级", len(result_df[result_df['优先级'].str.contains('高')]))
                with col3:
                    st.metric("📊 平均评分", int(result_df['综合评分'].mean()))
                with col4:
                    st.metric("📡 数据源", len(result_df['数据来源'].unique()))
                
                st.markdown("---")
                
                for _, row in result_df.iterrows():
                    score = row['综合评分']
                    priority = row['优先级']
                    p_class = "priority-high" if "高" in str(priority) else "priority-mid" if "中" in str(priority) else "priority-low"
                    p_label = "🔥 高优先级" if "高" in str(priority) else "📌 中优先级" if "中" in str(priority) else "💤 低优先级"
                    
                    st.markdown(f"""
                    <div class="company-card">
                        <div style="display:flex;justify-content:space-between;align-items:center;">
                            <div><strong>{row['公司名称']}</strong> <span class="{p_class}">{p_label}</span></div>
                            <div><span style="font-size:24px;font-weight:700;color:#667eea;">{score}</span></div>
                        </div>
                        <div style="margin-top:6px;display:flex;flex-wrap:wrap;gap:4px;">
                            <span class="tag">🎯 匹配度: {row.get('匹配度', 'N/A')}</span>
                            <span class="tag">📡 {row.get('数据来源', '')}</span>
                            {f'<span class="tag">👤 {row["创始人"]}</span>' if row.get('创始人') else ''}
                            {f'<span class="tag">📅 {row["成立时间"]}</span>' if row.get('成立时间') else ''}
                            {f'<span class="tag">💼 {row["招聘数"]}个岗位</span>' if row.get('招聘数', 0) > 0 else ''}
                        </div>
                        <div style="margin-top:6px;font-size:14px;color:#3c4043;">{row.get('理由', '')[:100]}</div>
                        <div style="font-size:13px;color:#667eea;">💡 {row.get('建议动作', '')}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                csv = result_df.to_csv(index=False).encode('utf-8-sig')
                st.download_button("📥 下载结果 (CSV)", data=csv, file_name=f"觅镜_结果_{datetime.now().strftime('%Y%m%d')}.csv", mime="text/csv", use_container_width=True)
