<template>
  <div :id="id" class="script-view">
    <!-- 显示加载文本 -->
    <ScriptLoadingText v-if="loading && !scriptConfig" :loading="loading" :script="selectedScript"/>
    <!-- 显示脚本描述 -->
    <p v-show="scriptDescription" class="script-description" v-html="formattedDescription"/>
    <!-- 参数视图 -->
    <ScriptParametersView v-if="hasParameters" ref="parametersView"/>
    <div class="actions-panel" :class="{ 'no-parameters': !hasParameters }">
      <!-- 执行脚本按钮 -->
      <button :disabled="!enableExecuteButton || scheduleMode"
              class="button-execute btn"
              v-bind:class="{ disabled: !enableExecuteButton }"
              @click="executeScript">
        Execute
      </button>
      <!-- 停止脚本按钮 -->
      <button :disabled="!enableStopButton"
              class="button-stop btn"
              v-bind:class="{
                    disabled: !enableStopButton,
                    'red lighten-1': !killEnabled,
                    'red darken-3': killEnabled}"
              @click="stopScript">
        {{ stopButtonLabel }}
      </button>
      <!-- 调度按钮 -->
      <div v-if="schedulable" class="button-gap"></div>
      <ScheduleButton v-if="schedulable" :disabled="!enableScheduleButton" @click="openSchedule"/>
    </div>
    <!-- 输入提示面板 -->
    <div v-if="inputPromptText" v-show="!hideExecutionControls" class="script-input-panel input-field">
      <label :for="'inputField-' + id" class="script-input-label">{{ inputPromptText }}</label>
      <input :id="'inputField-' + id" ref="inputField"
             class="script-input-field"
             type="text"
             v-on:keyup="inputKeyUpHandler">
    </div>
    <!-- 日志面板 -->
    <LogPanel v-show="showLog && !hasErrors && !hideExecutionControls" ref="logPanel" :outputFormat="outputFormat"/>
    <LogPanel v-if="preloadOutput && !showLog && !hasErrors && !hideExecutionControls"
              ref="preloadOutputPanel"
              :output-format="preloadOutputFormat"/>
    <!-- 验证错误面板 -->
    <div v-if="hasErrors" v-show="!hideExecutionControls" class="validation-panel">
      <h6 class="header">Validation failed. Errors list:</h6>
      <ul class="validation-errors-list">
        <li v-for="error in shownErrors">{{ error }}</li>
      </ul>
    </div>
    <!-- 可下载文件面板 -->
    <div v-if="downloadableFiles && (downloadableFiles.length > 0) && !scheduleMode" v-show="!hideExecutionControls"
         class="files-download-panel">
      <a v-for="file in downloadableFiles"
         :download="file.filename"
         :href="file.url"
         class="waves-effect btn-flat"
         target="_blank">
        {{ file.filename }}
        <i class="material-icons right">file_download</i>
      </a>
    </div>
    <!-- 调度持有人 -->
    <ScriptViewScheduleHolder v-if="!hideExecutionControls"
                              ref="scheduleHolder"
                              :scriptConfigComponentsHeight="scriptConfigComponentsHeight"
                              @close="scheduleMode = false"/>
  </div>
</template>


<script>
import LogPanel from '@/common/components/log_panel'
import {deepCloneObject, forEachKeyValue, isEmptyObject, isEmptyString, isNull} from '@/common/utils/common';
import ScheduleButton from '@/main-app/components/scripts/ScheduleButton';
import ScriptLoadingText from '@/main-app/components/scripts/ScriptLoadingText';
import ScriptViewScheduleHolder from '@/main-app/components/scripts/ScriptViewScheduleHolder';
import DOMPurify from 'dompurify';
import {marked} from 'marked';
import {mapActions, mapState} from 'vuex'
import {STATUS_DISCONNECTED, STATUS_ERROR, STATUS_EXECUTING, STATUS_FINISHED} from '../../store/scriptExecutor';
import ScriptParametersView from './script-parameters-view'

export default {
  data: function () {
    return {
      id: null, // 组件的唯一ID
      everStarted: false, // 是否曾经启动过
      shownErrors: [], // 显示的错误信息
      nextLogIndex: 0, // 下一个日志索引
      lastInlineImages: {}, // 上一次的内联图片
      scheduleMode: false, // 调度模式
      scriptConfigComponentsHeight: 0 // 脚本配置组件高度
    }
  },

  props: {
    hideExecutionControls: Boolean // 是否隐藏执行控制
  },

  mounted: function () {
    this.id = 'script-panel-' + this._uid; // 初始化唯一ID
  },

  components: {
    ScriptLoadingText,
    LogPanel,
    ScriptParametersView,
    ScheduleButton,
    ScriptViewScheduleHolder
  },

  computed: {
    ...mapState('scriptConfig', {
      scriptDescription: state => state.scriptConfig ? state.scriptConfig.description : '', // 脚本描述
      loading: 'loading', // 加载状态
      scriptConfig: 'scriptConfig', // 脚本配置
      outputFormat: state => state.scriptConfig ? state.scriptConfig.outputFormat : undefined, // 输出格式
      preloadOutput: state => state.preloadScript?.['output'], // 预加载输出
      preloadOutputFormat: state => state.preloadScript?.['format'] // 预加载输出格式
    }),
    ...mapState('scriptSetup', {
      parameterErrors: 'errors' // 参数错误
    }),
    ...mapState('executions', {
      currentExecutor: 'currentExecutor' // 当前执行器
    }),
    ...mapState('scripts', ['selectedScript']), // 选中的脚本

    hasErrors: function () {
      return !isNull(this.shownErrors) && (this.shownErrors.length > 0); // 是否有错误
    },

    formattedDescription: function () {
      // 格式化描述
      if (isEmptyString(this.scriptDescription)) {
        return '';
      }

      const descriptionHtml = DOMPurify.sanitize(marked.parse(this.scriptDescription, {gfm: true, breaks: true}));
      const paragraphRemoval = document.createElement('div');
      paragraphRemoval.innerHTML = descriptionHtml.trim();

      // 移除段落标签
      for (var i = 0; i < paragraphRemoval.childNodes.length; i++) {
        var child = paragraphRemoval.childNodes[i];
        if (child.tagName === 'P') {
          i += child.childNodes.length - 1;

          while (child.childNodes.length > 0) {
            paragraphRemoval.insertBefore(child.firstChild, child);
          }

          paragraphRemoval.removeChild(child);
        }
      }

      return paragraphRemoval.innerHTML;
    },

    enableExecuteButton() {
      // 启用执行按钮
      if (this.scheduleMode) {
        return false;
      }

      if (this.hideExecutionControls) {
        return false;
      }

      if (this.loading) {
        return false;
      }

      if (isNull(this.currentExecutor)) {
        return true;
      }

      return this.currentExecutor.state.status === STATUS_FINISHED
          || this.currentExecutor.state.status === STATUS_DISCONNECTED
          || this.currentExecutor.state.status === STATUS_ERROR;
    },

    enableScheduleButton() {
      // 启用调度按钮
      if (this.hideExecutionControls) {
        return false;
      }

      if (this.loading) {
        return false;
      }

      if (isNull(this.currentExecutor)) {
        return true;
      }

      return this.currentExecutor.state.status === STATUS_FINISHED
          || this.currentExecutor.state.status === STATUS_DISCONNECTED
          || this.currentExecutor.state.status === STATUS_ERROR;
    },

    enableStopButton() {
      return this.status === STATUS_EXECUTING; // 启用停止按钮
    },

    stopButtonLabel() {
      // 停止按钮标签
      if (this.status === STATUS_EXECUTING) {
        if (this.killEnabled) {
          return 'Kill';
        }

        if (!isNull(this.killEnabledTimeout)) {
          return 'Stop (' + this.killEnabledTimeout + ')';
        }
      }

      return 'Stop';
    },

    status() {
      return isNull(this.currentExecutor) ? null : this.currentExecutor.state.status; // 状态
    },

    showLog() {
      return !isNull(this.currentExecutor) && !this.scheduleMode; // 显示日志
    },

    downloadableFiles() {
      // 可下载文件
      if (!this.currentExecutor) {
        return [];
      }

      return this.currentExecutor.state.downloadableFiles;
    },

    inlineImages() {
      // 内联图片
      if (!this.currentExecutor) {
        return {};
      }

      return this.currentExecutor.state.inlineImages;
    },

    inputPromptText() {
      // 输入提示文本
      if (this.status !== STATUS_EXECUTING) {
        return null;
      }

      return this.currentExecutor.state.inputPromptText;
    },

    logChunks() {
      // 日志块
      if (!this.currentExecutor) {
        return [];
      }

      return this.currentExecutor.state.logChunks;
    },

    killEnabled() {
      // 启用杀死
      return !isNull(this.currentExecutor) && this.currentExecutor.state.killEnabled;
    },

    killEnabledTimeout() {
      // 启用杀死超时
      return isNull(this.currentExecutor) ? null : this.currentExecutor.state.killTimeoutSec;
    },

    schedulable() {
      // 可调度
      return this.scriptConfig && this.scriptConfig.schedulable;
    },

    hasParameters() {
      // 是否有参数
      return this.scriptConfig && this.scriptConfig.parameters && this.scriptConfig.parameters.length > 0;
    }
  },

  methods: {
    inputKeyUpHandler: function (event) {
      // 输入键盘按键处理
      if (event.keyCode === 13) {
        const inputField = this.$refs.inputField;

        this.sendUserInput(inputField.value);

        inputField.value = '';
      }
    },

    validatePreExecution: function () {
      // 验证执行前的参数
      this.shownErrors = [];

      const errors = this.parameterErrors;
      if (!isEmptyObject(errors)) {
        forEachKeyValue(errors, (paramName, error) => {
          this.shownErrors.push(paramName + ': ' + error);
        });
        return false;
      }

      return true;
    },

    executeScript: function () {
      // 执行脚本
      if (!this.validatePreExecution()) {
        return;
      }

      this.startExecution();
    },

    openSchedule: function () {
      // 打开调度
      if (!this.validatePreExecution()) {
        return;
      }

      this.$refs.scheduleHolder.open();
      this.scheduleMode = true;
    },

    ...mapActions('executions', {
      startExecution: 'startExecution' // 开始执行脚本
    }),

    stopScript() {
      // 停止脚本
      if (isNull(this.currentExecutor)) {
        return;
      }

      if (this.killEnabled) {
        this.$store.dispatch('executions/' + this.currentExecutor.state.id + '/killExecution');
      } else {
        this.$store.dispatch('executions/' + this.currentExecutor.state.id + '/stopExecution');
      }
    },

    sendUserInput(value) {
      // 发送用户输入
      if (isNull(this.currentExecutor)) {
        return;
      }

      this.$store.dispatch('executions/' + this.currentExecutor.state.id + '/sendUserInput', value);
    },

    setLog: function (text) {
      // 设置日志
      this.$refs.logPanel.setLog(text);
    },

    appendLog: function (text) {
      // 追加日志
      this.$refs.logPanel.appendLog(text);
    }
  },

  watch: {
    inputPromptText: function (value) {
      // 监听输入提示文本
      if (isNull(value) && isNull(this.$refs.inputField)) {
        return;
      }

      var fieldUpdater = function () {
        this.$refs.inputField.value = '';
        if (!isNull(value)) {
          this.$refs.inputField.focus();
        }
      }.bind(this);

      if (this.$refs.inputField) {
        fieldUpdater();
      } else {
        this.$nextTick(fieldUpdater);
      }
    },

    logChunks: {
      immediate: true,
      handler(newValue, oldValue) {
        // 监听日志块
        const updateLog = () => {
          if (isNull(newValue)) {
            this.setLog('');
            this.nextLogIndex = 0;

            return;
          }

          if (newValue !== oldValue) {
            this.setLog('');
            this.nextLogIndex = 0;
          }

          for (; this.nextLogIndex < newValue.length; this.nextLogIndex++) {
            const logChunk = newValue[this.nextLogIndex];

            this.appendLog(logChunk);
          }
        }

        if (isNull(this.$refs.logPanel)) {
          this.$nextTick(updateLog);
        } else {
          updateLog();
        }
      }
    },

    preloadOutput: {
      handler(newValue, _) {
        // 监听预加载输出
        this.$nextTick(() => {
          if (this.$refs.preloadOutputPanel) {
            this.$refs.preloadOutputPanel.setLog(newValue);
          }
        })
      }
    },

    inlineImages: {
      handler(newValue, oldValue) {
        // 监听内联图片
        const logPanel = this.$refs.logPanel;

        forEachKeyValue(this.lastInlineImages, (key, value) => {
          if (!newValue.hasOwnProperty(key)) {
            logPanel.removeInlineImage(key);
          } else if (value !== newValue[key]) {
            logPanel.setInlineImage(key, value);
          }
        });

        forEachKeyValue(newValue, (key, value) => {
          if (!this.lastInlineImages.hasOwnProperty(key)) {
            logPanel.setInlineImage(key, value);
          }
        });

        this.lastInlineImages = deepCloneObject(newValue);
      }
    },

    scriptConfig: {
      immediate: true,
      handler() {
        // 监听脚本配置
        this.shownErrors = []

        this.$nextTick(() => {
          // 200 is a rough height for headers,buttons, description, etc.
          const otherElemsHeight = 200;

          if (isNull(this.$refs.parametersView)) {
            this.scriptConfigComponentsHeight = otherElemsHeight;
            return;
          }

          const paramHeight = this.$refs.parametersView.$el.clientHeight;

          this.scriptConfigComponentsHeight = paramHeight + otherElemsHeight;
        })
      }
    },

    status: {
      handler(newStatus) {
        // 监听状态
        if (newStatus === STATUS_FINISHED) {
          this.$store.dispatch('executions/' + this.currentExecutor.state.id + '/cleanup');
        }
      }
    }
  }
}
</script>

<style scoped>
.script-view {
  display: flex;
  flex-direction: column;
  flex: 1 1 0;

  /* (firefox)
      we have to specify min-size explicitly, because by default it's content size.
      It means, that when child content is larger than parent, it will grow out of parent
      See https://drafts.csswg.org/css-flexbox/#min-size-auto
      and https://bugzilla.mozilla.org/show_bug.cgi?id=1114904
  */
  min-height: 0;
}

.actions-panel,
.files-download-panel {
  flex: 0 0 content;
}

.script-description,
.script-loading-text {
  margin: 0;
}

.actions-panel {
  margin-top: 8px;
  display: flex;
}

.actions-panel.no-parameters {
  margin-top: 0; /* 当没有参数时，移除顶部的间距 */
}

.actions-panel > .button-gap {
  flex: 3 1 1px;
}

.button-execute {
  flex: 4 1 312px;
}

.button-stop {
  margin-left: 16px;
  flex: 1 1 104px;
  color: var(--font-on-primary-color-main)
}

.schedule-button {
  margin-left: 32px;
  flex: 1 0 auto;
}

.script-input-panel {
  margin-top: 20px;
  margin-bottom: 0;
}

.script-input-panel input[type=text] {
  margin: 0;
  width: 100%;
  height: 1.5em;
  font-size: 1.5rem;
}

.script-input-panel > label {
  transform: translateY(-30%);
  margin-left: 2px;
}

.script-input-panel.input-field > label.active {
  color: var(--primary-color);
  transform: translateY(-70%) scale(0.8);
}

.validation-panel {
  overflow-y: auto;
  flex: 1;

  margin: 20px 0 8px;
}

.validation-panel .header {
  padding-left: 0;
}

.validation-errors-list {
  margin-left: 12px;
  margin-top: 8px;
}

.validation-errors-list li {
  color: #F44336;
}

.files-download-panel {
  margin-top: 12px;
}

.files-download-panel a {
  color: var(--primary-color);
  padding-left: 16px;
  padding-right: 16px;
  margin-right: 8px;
  text-transform: none;
}

.files-download-panel a > i {
  margin-left: 8px;
  vertical-align: middle;
  font-size: 1.5em;
  line-height: 2em;
}

.script-view >>> .log-panel {
  margin-top: 12px;
}
</style>
