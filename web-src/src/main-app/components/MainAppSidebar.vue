<template>
  <div class="main-app-sidebar">
    <div class="list-header">
      <router-link :class="{
                    'header-gt-15-chars' : serverName && serverName.length >= 15,
                    'header-gt-18-chars' : serverName && serverName.length >= 18,
                    'header-gt-21-chars' : serverName && serverName.length >= 21
      }" :title="versionString"
                   class="header server-header"
                   to="/">
        {{ serverName || 'Script server' }}
      </router-link>

      <SearchPanel v-model="searchText"/>

      <div class="header-link">
        <a v-if="adminUser" class="primary-color-text" href="admin.html">
          <i class="material-icons">settings</i>
        </a>
        <a v-else href="https://py.cschub.vip/" target="_blank">
          <svg aria-hidden="true" class="svg-icon github-icon" height="20px" viewBox="0 0 16 16" width="20px">
            <path
                d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"/>
          </svg>
        </a>
      </div>
    </div>

    <ScriptsList :search-text="searchText"/>

    <div class="bottom-panel">
      <router-link
        class="waves-effect btn-flat history-button primary-color-text"
        to="/history"
      >
        History
      </router-link>
      <a
        class="waves-effect btn-flat ssrs-button"
        href="https://ssrs.cschub.vip/Reports/browse"
        target="_blank"
      >
        SSRS
      </a>
      <a
        class="waves-effect btn-flat label-button"
        href="https://bt.cschub.vip/bartender"
        target="_blank"
      >
        Label
      </a>
    </div>

    <!-- 添加分隔线 -->
    <div class="separator-line"></div>

    <div v-if="authEnabled" class="bottom-panel logout-panel">
      <span class="username">{{ username }}</span>
      <a
        class="btn-icon-flat waves-effect logout-button waves-circle"
        @click="logout"
      >
        <i class="material-icons primary-color-text">power_settings_new</i>
      </a>
    </div>
  </div>
</template>


<script>
import {mapActions, mapState} from 'vuex';
import ScriptsList from './scripts/ScriptsList';
import SearchPanel from './SearchPanel';

export default {
  name: 'MainAppSidebar',
  components: {
    SearchPanel,
    ScriptsList
  },

  data() {
    return {
      searchText: '',
    }
  },

  computed: {
    ...mapState('serverConfig', {
      versionString: state => state.version ? 'v' + state.version : null,
      serverName: 'serverName'
    }),
    ...mapState('auth', {
      adminUser: 'admin',
      username: 'username',
      authEnabled: 'enabled'
    })
  },

  methods: {
    ...mapActions(['logout'])
  }
}
</script>

<style scoped>
.list-header {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: flex-start;
  border-bottom: 5px solid transparent;
  flex-shrink: 0;
  position: relative;
}

.server-header {
  flex-grow: 1;
  margin-left: 0.4rem;
  font-size: 1.64rem;
  padding: 0.8rem;
  font-weight: 300;
  line-height: 110%;
  color: var(--font-color-main);
  min-width: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  word-break: break-all;
  transition: font-size 0.3s;
}

.server-header.header-gt-15-chars {
  font-size: 1.45rem;
}

.server-header.header-gt-18-chars {
  font-size: 1.25rem;
}

.server-header.header-gt-21-chars {
  font-size: 1.2rem;
}

.main-app-sidebar {
  height: 100%;
  background: var(--background-color);
  display: flex;
  flex-direction: column;
}

.header-link {
  margin: 0 1rem;
  display: flex;
  line-height: 0;
}

.header-link .svg-icon {
  width: 24px;
  height: 24px;
}

.header-link .svg-icon path {
  fill: var(--primary-color);
}

.history-button {
  line-height: 2.5em;
  text-align: center;
  transition: background-color 0.3s;
  color: var(--primary-color);
}

.history-button:hover {
  background-color: var(--hover-background-color);
}

.ssrs-button,
.label-button {
  line-height: 2.5em;
  text-align: center;
  transition: background-color 0.3s;
  color: var(--primary-color);
  text-decoration: none;
}

.ssrs-button:hover,
.label-button:hover {
  background-color: transparent;
}

.bottom-panel {
  display: flex;
  align-items: center;
  justify-content: center; /* 调整为 center 以使内容居中 */
  padding: 0.5rem 1rem;
  border-top: 1px solid var(--separator-color);
  height: 2.5em;  /* 统一行高 */
}

.logout-panel {
  border-top: none;  /* 移除 logout-panel 的顶部边框 */
}

.logout-button {
  margin-left: 8px;
  transition: background-color 0.3s;
}

.username {
  margin-right: 8px;
  color: var(--font-color-main);
}

.separator-line {
  border-top: 1px solid var(--separator-color); /* 分隔线样式 */
  width: 100%;
}
</style>







